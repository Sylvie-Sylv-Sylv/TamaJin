# TamaJin

An OOP Python Game Engine aimed for clean and scalable system design suited for game development with the solidity of the Java programming language.

---

## Design Philosophies

### System Design Principles

* Consistency

---

Here are the elaborations for those core OOP design philosophies, formatted for easy copying:

### OOP Design Philosophies

#### SOLID

The five pillars of readable, flexible, and maintainable object-oriented code.

* **S - Single Responsibility Principle:** A class should have one, and only one, reason to change. It should focus on a single task or functionality.
* **O - Open/Closed Principle:** Software entities should be open for extension but closed for modification. You should be able to add new features without breaking existing code.
* **L - Liskov Substitution Principle:** Objects of a superclass should be replaceable with objects of its subclasses without affecting the correctness of the program.
* **I - Interface Segregation Principle:** No client should be forced to depend on methods it does not use. It is better to have many specific interfaces than one general-purpose "fat" interface.
* **D - Dependency Inversion Principle:** Depend on abstractions, not concretions. High-level modules should not depend on low-level modules; both should depend on interfaces.

#### DRY

**"Don't Repeat Yourself"** — A principle aimed at reducing the repetition of software patterns.

* **Centralized Logic:** Every piece of knowledge or logic must have a single, unambiguous, authoritative representation within a system.
* **Maintainability:** When logic needs to change, you only have to update it in one place, reducing the risk of bugs and inconsistencies.
* **Abstraction:** Encourages the use of functions, loops, and classes to handle repetitive tasks instead of "copy-pasting" code blocks.

#### KISS

**"Keep It Simple, Stupid"** — A design principle stating that systems work best if they are kept simple rather than made complicated.

* **Avoid Over-Engineering:** Don't build complex solutions for simple problems or try to account for "future needs" that may never happen (YAGNI).
* **Readability:** Code should be written so that it can be easily understood by others (or yourself in six months) without an instruction manual.
* **Reduced Surface Area:** Fewer moving parts and simpler logic paths lead to fewer bugs and easier testing.

#### Data-driven Composition over Composition over Inheritance

Why we favor data-driven composition over traditional composition and favor data-driven composition over inheritance

* **Solves the "Diamond Problem":** It avoids the technical conflicts and ambiguity that arise when a class tries to inherit from multiple parents with overlapping methods.
* **Enables Runtime Flexibility:** Through data-driven composition, an entity’s behavior and data can be swapped or modified while the game is running, unlike the static, "locked-in" nature of inheritance.
* **Promotes Modularity:** Components act as independent, reusable building blocks, making the codebase easier to maintain, test, and scale without affecting unrelated systems.
* **Replaces Rigid Trees with Flexible Graphs:** It shifts the architecture from a strict taxonomic hierarchy to a flexible graph of behaviors. This creates a "meta" layer for entity definition, allowing for the creation of diverse variants by simply assembling components.
* **Preserves Inheritance for "Is-A" Specialization:** Inheritance is reserved for cases where an object is a specialized version of a base type by definition—where the core data is unique and intrinsically specific to that lineage, and every child class strictly extends that fundamental identity without needing to mix in unrelated traits.

---

### Supported arhitectural styles

#### Monolithic

* This architecture is crucial for prototyping.

#### Microservices

* This architecture is crucial for managing large games.

#### Event driven architecture

* This architecture is especially useful for games.

---

## Features