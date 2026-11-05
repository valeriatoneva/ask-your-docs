# Standalone components

A standalone component declares its own dependencies in its imports array, so it does not need to be declared in an NgModule. You mark a component as standalone, and from recent Angular versions this is the default behaviour.

Standalone components make applications easier to understand because everything a component needs is listed next to the component itself. They also make lazy loading simpler: a route can load a component directly with loadComponent, and the code for that component is split into its own bundle that is downloaded only when the route is visited.

For libraries of shared UI, standalone components are convenient because a consumer imports only the components it actually uses, which helps tree shaking and keeps bundles small. When a shared library is used by many developers, keep each component focused, give it clear inputs and outputs, and avoid hidden dependencies on global services so that it can be reused and tested in isolation.

Existing NgModule based code can be migrated step by step. Standalone components and modules can live side by side during the migration.
