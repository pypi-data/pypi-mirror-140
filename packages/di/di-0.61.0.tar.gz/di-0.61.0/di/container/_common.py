from __future__ import annotations

import inspect
from collections import deque
from contextlib import contextmanager
from typing import (
    Any,
    ContextManager,
    Deque,
    Dict,
    Generator,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    TypeVar,
)

from graphlib2 import TopologicalSorter

from di._utils.execution_planning import SolvedDependantCache, plan_execution
from di._utils.inspect import get_type
from di._utils.scope_validation import validate_scopes
from di._utils.state import ContainerState
from di._utils.task import Task
from di._utils.topsort import topsort
from di.api.dependencies import CacheKey, DependantBase, DependencyParameter
from di.api.executor import AsyncExecutorProtocol, SyncExecutorProtocol
from di.api.providers import DependencyProvider
from di.api.scopes import Scope
from di.api.solved import SolvedDependant
from di.container._bind_hook import BindHook
from di.exceptions import SolvingError, WiringError

DependencyType = TypeVar("DependencyType")


class ContainerCommon:
    __slots__ = ("_scopes", "_register_hooks")

    _scopes: Sequence[Scope]
    _register_hooks: List[BindHook]

    def __init__(
        self,
        scopes: Sequence[Scope],
    ):
        self._scopes = tuple(scopes)
        self._register_hooks = []

    @property
    def scopes(self) -> Sequence[Scope]:
        return self._scopes

    @property
    def current_scopes(self) -> Sequence[Scope]:
        return tuple(self._state.stacks.keys())

    @property
    def _state(self) -> ContainerState:
        raise NotImplementedError

    def register_bind_hook(
        self,
        hook: BindHook,
    ) -> ContextManager[None]:
        """Replace a dependency provider with a new one.

        This can be used as a function (for a permanent bind, cleared when `scope` is exited)
        or as a context manager (the bind will be cleared when the context manager exits).

        Binds are only identified by the identity of the callable and do not take into account
        the scope or any other data from the dependency they are replacing.
        """

        self._register_hooks.append(hook)

        @contextmanager
        def unbind() -> Generator[None, None, None]:
            try:
                yield
            finally:
                self._register_hooks.remove(hook)

        return unbind()

    def bind_by_type(
        self,
        provider: DependantBase[Any],
        dependency: type,
        *,
        covariant: bool = False,
    ) -> ContextManager[None]:
        def hook(
            param: Optional[inspect.Parameter], dependant: DependantBase[Any]
        ) -> Optional[DependantBase[Any]]:
            if dependant.call is dependency:
                return provider
            if param is None:
                return None
            type_annotation_option = get_type(param)
            if type_annotation_option is None:
                return None
            type_annotation = type_annotation_option.value
            if type_annotation is dependency:
                return provider
            if covariant:
                if inspect.isclass(type_annotation) and inspect.isclass(dependency):
                    if dependency in type_annotation.__mro__:
                        return provider
            return None

        return self.register_bind_hook(hook)

    def solve(
        self,
        dependency: DependantBase[DependencyType],
    ) -> SolvedDependant[DependencyType]:
        """Solve a dependency.

        Returns a SolvedDependant that can be executed to get the dependency's value.
        """
        # If the dependency itself is a bind, replace it
        for hook in self._register_hooks:
            match = hook(None, dependency)
            if match:
                dependency = match

        dependants: Dict[CacheKey, DependantBase[Any]] = {}
        # DAG mapping dependants to their dependendencies
        dep_dag: Dict[DependantBase[Any], List[DependantBase[Any]]] = {}
        # The same DAG as above but including parameters (inspect.Parameter instances)
        param_graph: Dict[DependantBase[Any], List[DependencyParameter]] = {}

        def get_params(
            dep: DependantBase[Any],
        ) -> List[DependencyParameter]:
            # get parameters and swap them out w/ binds when they
            # exist as a bound value
            params = dep.get_dependencies().copy()
            for idx, param in enumerate(params):
                for hook in self._register_hooks:
                    match = hook(param.parameter, param.dependency)
                    if match is not None:
                        param = param._replace(dependency=match)
                params[idx] = param
                if param.parameter is not None:
                    if (
                        param.dependency.call is None
                        and param.parameter.default is param.parameter.empty
                    ):
                        raise WiringError(
                            f"The parameter {param.parameter.name} to {dep.call} has no dependency marker,"
                            " no type annotation and no default value."
                            " This will produce a TypeError when this function is called."
                            " You must either provide a dependency marker, a type annotation or a default value."
                        )
            return params

        # Do a DFS of the DAG checking constraints along the way
        q: Deque[DependantBase[Any]] = deque((dependency,))
        seen: Set[DependantBase[Any]] = set()
        while q:
            dep = q.popleft()
            seen.add(dep)
            cache_key = dep.cache_key
            if cache_key in dependants:
                other = dependants[cache_key]
                if other.scope != dep.scope:
                    raise SolvingError(
                        f"The dependency {dep.call} is used with multiple scopes"
                        f" ({dep.scope} and {other.scope}); this is not allowed."
                    )
                continue
            dependants[cache_key] = dep
            params = get_params(dep)
            param_graph[dep] = params
            dep_dag[dep] = []
            for param in params:
                predecessor_dep = param.dependency
                dep_dag[dep].append(predecessor_dep)
                if predecessor_dep not in seen:
                    q.append(predecessor_dep)
        # Filter out any dependencies that do not have a call
        # These do not become tasks since they don't need to be computed
        computable_param_graph = {
            dep: [
                param for param in param_graph[dep] if param.dependency.call is not None
            ]
            for dep in param_graph
            if dep.call is not None
        }
        # Order the Dependant's topologically so that we can create Tasks
        # with references to all of their children
        dep_topsort = topsort(
            {
                dep.cache_key: [p.dependency.cache_key for p in params]
                for dep, params in computable_param_graph.items()
            }
        )
        # Create a seperate TopologicalSorter to hold the Tasks
        ts: TopologicalSorter[Task] = TopologicalSorter()
        tasks = self._build_tasks(
            computable_param_graph,
            (dependants[key] for key_group in dep_topsort for key in key_group),
            ts,
        )
        ts.prepare()
        container_cache = SolvedDependantCache(
            root_task=tasks[dependency.cache_key],
            topological_sorter=ts,
        )
        validate_scopes(
            self._scopes,
            dep_dag,
        )
        solved = SolvedDependant(
            dependency=dependency,
            dag=param_graph,
            container_cache=container_cache,
        )
        return solved

    def _build_tasks(
        self,
        dag: Dict[
            DependantBase[Any],
            List[DependencyParameter],
        ],
        topsorted: Iterable[DependantBase[Any]],
        ts: TopologicalSorter[Task],
    ) -> Dict[CacheKey, Task]:
        tasks: Dict[CacheKey, Task] = {}
        task_id = 0
        for dep in topsorted:
            positional: List[Task] = []
            keyword: Dict[str, Task] = {}
            for param in dag[dep]:
                if param.parameter is not None:
                    task = tasks[param.dependency.cache_key]
                    if param.parameter.kind is param.parameter.KEYWORD_ONLY:
                        keyword[param.parameter.name] = task
                    else:
                        positional.append(task)

            positional_parameters = tuple(positional)
            keyword_parameters = tuple((k, v) for k, v in keyword.items())

            assert dep.call is not None
            tasks[dep.cache_key] = task = Task(
                scope=dep.scope,
                call=dep.call,
                use_cache=dep.use_cache,
                cache_key=dep.cache_key,
                dependant=dep,
                task_id=task_id,
                positional_parameters=positional_parameters,
                keyword_parameters=keyword_parameters,
            )
            task_id += 1
            ts.add(task, *(tasks[p.dependency.cache_key] for p in dag[dep]))
        return tasks

    def execute_sync(
        self,
        solved: SolvedDependant[DependencyType],
        executor: SyncExecutorProtocol,
        *,
        values: Optional[Mapping[DependencyProvider, Any]] = None,
    ) -> DependencyType:
        """Execute an already solved dependency.

        This method is synchronous and uses a synchronous executor,
        but the executor may still be able to execute async dependencies.
        """
        results, leaf_tasks, execution_state, root_task = plan_execution(
            stacks=self._state.stacks,
            cache=self._state.cached_values,
            solved=solved,
            values=values,
        )
        if root_task.task_id not in results:
            executor.execute_sync(leaf_tasks, execution_state)  # type: ignore[union-attr]
        return results[root_task.task_id]  # type: ignore[no-any-return]

    async def execute_async(
        self,
        solved: SolvedDependant[DependencyType],
        executor: AsyncExecutorProtocol,
        *,
        values: Optional[Mapping[DependencyProvider, Any]] = None,
    ) -> DependencyType:
        """Execute an already solved dependency."""
        results, leaf_tasks, execution_state, root_task = plan_execution(
            stacks=self._state.stacks,
            cache=self._state.cached_values,
            solved=solved,
            values=values,
        )
        if root_task.task_id not in results:
            await executor.execute_async(leaf_tasks, execution_state)  # type: ignore[union-attr]
        return results[root_task.task_id]  # type: ignore[no-any-return]
