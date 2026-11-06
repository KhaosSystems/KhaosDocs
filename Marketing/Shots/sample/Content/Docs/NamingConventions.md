# Naming Conventions

Names sort, search and review better when they all follow one pattern:

```
Prefix_AssetName_Variant
SM_Crate_Large
T_Crate_Large_D
BP_Door_Sliding
```

## Prefixes

- `SM_` static mesh
- `SK_` skeletal mesh
- `T_` texture
- `M_` material, `MI_` material instance
- `BP_` blueprint
- `WBP_` widget blueprint

## Texture suffixes

- `_D` base colour
- `_N` normal
- `_ORM` occlusion, roughness, metallic

## Rules of thumb

Use *PascalCase*, never spaces. Keep variants at the end. If a reviewer asks what a name means, the name is wrong.
