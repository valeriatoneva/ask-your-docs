# RxJS basics

RxJS models asynchronous data as streams called observables. An observable does nothing until somebody subscribes to it, and it can emit many values over time, then complete or fail with an error. HTTP requests, user input events and timers are all natural observables.

Operators transform streams. The map operator changes each value, filter drops values, and debounceTime waits until the user has stopped typing before emitting, which is useful for search boxes. To combine requests, switchMap cancels the previous inner request when a new value arrives, so it is the right choice for typeahead search. The mergeMap operator runs inner requests in parallel, and concatMap runs them one after another in order.

Memory leaks happen when a subscription is never cleaned up. Unsubscribe when a component is destroyed, or use the async pipe in the template, which subscribes and unsubscribes automatically. The takeUntilDestroyed operator is another safe way to end a subscription when the component goes away.

Subjects are both an observable and an observer. A BehaviorSubject keeps the latest value and gives it immediately to new subscribers, which makes it useful for simple shared state.
