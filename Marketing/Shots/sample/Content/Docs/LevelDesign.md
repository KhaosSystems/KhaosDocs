# Level Design

How a level goes from an idea to something we can ship.

## Stages

### Greybox

Block out the route with the kit in `Environment/Blockout`. No art yet: the only question is whether it plays well.

### First art pass

Swap blockout pieces for real props. Keep the collision of the greybox until the route is signed off.

### Lighting

Lighting starts only after the art pass. Use one `Lighting` sublevel per level so it can be reviewed alone.

## Checklist before review

- The player can't get stuck anywhere on the route.
- Every door has a reason to exist.
- The level loads in under ten seconds on the target machine.

## Performance budgets

Keep draw calls under **2,000** and triangles under **3 million** on screen.

## Related

- [Naming Conventions](NamingConventions.md)
- [Build and Release](BuildAndRelease.md)
