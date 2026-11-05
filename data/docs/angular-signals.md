# Angular signals

A signal is a wrapper around a value that tells Angular exactly when that value changes. You create one with the signal function and read it by calling it like a function. To change the value you call set, or update when the new value depends on the old one.

A computed signal derives a new value from other signals. It is lazy and cached: it only recalculates when one of the signals it reads has changed, and only when somebody reads it again. This makes computed signals a good place for values such as a filtered list or a total price.

An effect runs a side effect whenever the signals it reads change, for example writing a value to local storage or logging. Effects should not be used to copy one signal into another; use a computed signal for that instead.

Signals make change detection more precise. Angular can update only the parts of a template that depend on a changed signal instead of checking the whole component tree. Signals are synchronous and always hold a current value, which is the main difference from observables: an observable may never emit, while a signal can always be read right now.
