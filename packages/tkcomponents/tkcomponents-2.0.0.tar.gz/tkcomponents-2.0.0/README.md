# tkcomponents

###### An OOP framework for Tkinter, inspired by React

## Quickstart

### Setup

Below is an example of a custom component, a number label which updates its value periodically.

```python
from tkinter import Label, IntVar

from tkcomponents import Component


class Counter(Component):
    def __init__(self, container):
        super().__init__(container, update_interval_ms=250)  # The component will update 4 times per second

        self._count__var = IntVar()
        self._count__var.set(0)

    @property
    def _needs_render(self):
        return self._count__var.get() % 5 == 0  # A full re-render will trigger on multiples of 5

    def _update(self):
        current_count = self._count__var.get()

        self._count__var.set(current_count+1)  # The counter will increase by 1 each update, a total of +4 per second

    def _render(self):
        Label(self._frame, textvariable=self._count__var).pack()
```

### App Boilerplate
```python
from tkinter import Tk


class App:
    def __init__(self):
        self.window = Tk()

        Counter(self.window).render().pack()  # Note that .render() is called from outside the component, not ._render()

        self.window.mainloop()

if __name__ == "__main__":
    App()
```
