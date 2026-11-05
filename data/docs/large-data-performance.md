# Performance with large datasets

Rendering tens of thousands of rows at once makes a page slow, because the browser has to create and lay out every element. Virtual scrolling solves this by rendering only the rows that are visible in the viewport plus a small buffer. As the user scrolls, rows are reused with new data, so the number of elements in the page stays small and constant.

Lazy loading delays work until it is needed. Heavy widgets can be loaded with the defer block, which loads a component when it enters the viewport or when the browser is idle. Data can also be fetched in pages instead of all at once, with the server returning a fixed number of records per request.

Server side pagination needs a stable sort order. If the ordering is not deterministic, the same record can appear on two pages or be skipped, so always sort by a unique column such as an id. Skip and take are used to select a page, and a separate count query returns the total number of records for the pager.

Measure before optimising. Use the browser profiler to find slow renders, and avoid recalculating derived values on every change detection cycle by caching them, for example with computed signals.
