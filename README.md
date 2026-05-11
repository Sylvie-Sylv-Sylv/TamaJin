# TamaJin

An OOP Python Game Engine aimed for clean and scalable system design suited for game development with the solidity of the Java programming language.

---

## Design Philosophies

### System Design Principles

* Consistency

---

### OOP Design Philosophies

#### SOLID

#### DRY

#### KISS

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
