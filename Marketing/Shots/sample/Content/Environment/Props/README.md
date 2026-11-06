# Props

Shared set dressing. Everything here is used in more than one level.

## Adding a prop

1. Name it `SM_Thing_Variant`, see [Naming Conventions](../../Docs/NamingConventions.md).
2. Put its materials in `Materials`, not beside the mesh.
3. Give it simple collision before you submit it.

## Sizes

- **Small** props fit in one hand and have no collision.
- **Medium** props block the player and stay under 2 metres.
- **Large** props belong in `Architecture`.

> Lamps are props, but their lights belong to the level, so don't parent one to the mesh.

## Ask before changing

The `SM_Door` family is referenced by every level. Talk to the level team first.
