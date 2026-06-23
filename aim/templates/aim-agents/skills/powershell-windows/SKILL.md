---
name: powershell-windows
description: Collects the syntax rules and failure modes that trip up PowerShell scripting on Windows -- operator grouping, ASCII-only output, null guards, JSON depth, and error-handling structure. It pairs each pitfall with the corrected form so scripts run reliably under Set-StrictMode. Use it when authoring or debugging PowerShell on Windows; it does not apply to macOS or Linux shells.
---

# PowerShell on Windows

PowerShell has a handful of sharp edges that bite predictably. The rules below are not stylistic preferences -- ignoring them produces parser errors or silent wrong behavior.

## Group cmdlet calls inside conditions

When a cmdlet result feeds a logical operator, wrap the call in parentheses. The parser otherwise treats `-or`/`-and` as a parameter to the cmdlet.

```powershell
# Breaks: -or is read as an argument to Test-Path
if (Test-Path $a -or Test-Path $b) { ... }

# Works: each call is its own grouped expression
if ((Test-Path $a) -or (Test-Path $b)) { ... }

# Same rule with a comparison on one side
if ((Get-Item $p) -and ($count -eq 5)) { ... }
```

## Stick to ASCII in script output

Non-ASCII glyphs (emoji, check marks, box drawing) cause "Unexpected token" errors on many Windows consoles and code pages. Use bracketed ASCII tags instead.

| Meaning | Avoid | Use |
|---------|-------|-----|
| Success | check / tick marks | `[OK]` `[+]` |
| Failure | cross / red circle | `[X]` `[!]` |
| Warning | warning sign | `[WARN]` `[*]` |
| Info | info symbol | `[INFO]` `[i]` |
| In progress | hourglass | `[...]` |

## Guard against null before dereferencing

Touching a property or method on `$null` throws -- and under `Set-StrictMode` even reading an unset variable does. Check first.

```powershell
# Risky
if ($items.Count -gt 0) { ... }
$len = $name.Length

# Safe
if ($items -and $items.Count -gt 0) { ... }
if ($name) { $len = $name.Length }
```

## Pull deep expressions out of strings

Interpolating a multi-hop property chain inside a string is fragile. Assign it to a variable, then interpolate the variable.

```powershell
# Fragile
Write-Output "City: $($order.customer.address.city)"

# Clear
$city = $order.customer.address.city
Write-Output "City: $city"
```

## Choose the right error preference

`$ErrorActionPreference` sets how non-terminating errors behave:

| Value | Fits |
|-------|------|
| `Stop` | development -- fail loudly and early |
| `Continue` | production scripts that should push through |
| `SilentlyContinue` | spots where an error is expected and fine |

In `try`/`catch`: do not `return` from inside the `try`, put cleanup in `finally`, and return after the whole block resolves.

## Build paths safely

Prefer `Join-Path` over hand-concatenated strings -- it handles separators correctly and reads clearly.

```powershell
$literal  = "C:\Users\Sam\report.txt"            # fixed location
$inHome   = Join-Path $env:USERPROFILE "report.txt"
$relative = Join-Path $ScriptDir "data"
```

## Work with arrays correctly

```powershell
$items = @()                 # initialize empty
$items += $next              # append (fine for small sets)
$list.Add($next) | Out-Null  # ArrayList: suppress the index it returns
```

## Always set JSON depth

`ConvertTo-Json` truncates nested structures at a shallow default. Pass `-Depth` whenever objects nest.

```powershell
# Loses nested data
$obj | ConvertTo-Json

# Keeps it
$obj | ConvertTo-Json -Depth 10

# Round-tripping a file
$data = Get-Content "config.json" -Raw | ConvertFrom-Json
$data | ConvertTo-Json -Depth 10 | Out-File "config.json" -Encoding UTF8
```

## Decoding common errors

| Message | Likely cause | Fix |
|---------|--------------|-----|
| parameter `'or'` not found | cmdlet not parenthesized | wrap each call in `()` |
| Unexpected token | non-ASCII character | use ASCII tags |
| property cannot be found on null | dereferenced `$null` | null-check first |
| cannot convert value | type mismatch | coerce with `.ToString()` etc. |

## Starting skeleton

```powershell
Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

try {
    # work goes here
    Write-Output "[OK] Completed"
    exit 0
}
catch {
    Write-Warning "Failed: $_"
    exit 1
}
```

The recurring theme: parenthesize cmdlet calls in conditions, keep output ASCII, and never assume a value is non-null. Those three cover the majority of PowerShell breakage on Windows.
