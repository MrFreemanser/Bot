---
description: Implements Guild Points function which are bound to each server.
---

# Points

Members can earn points in different servers by chatting normally in text channels where the bot can read their messages. They can also claim their daily points.

These points can be redeemed to unlock various perks in the server set by the administrators like a role from Role Shop.

## ;points

Displays Guild Points earned by you or specified member.

```yaml
Usage:
;points [member]
```

### ;points daily

Lets you claim your daily золотых монет. Specify any member to let them have your daily золотых монет.

```yaml
Usage:
;points daily [member]
```

### ;points credit

Transfer your points to specified member.

```yaml
Aliases:
- transfer
- give

Usage:
points credit <points> <member>
```

