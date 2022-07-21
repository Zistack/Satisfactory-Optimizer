# Satisfactory Optimizer

A simple command-line utility for planning factories in Satisfactory.
In addition to being a full teplacement for online calculators (albeit with a less convenient user interface), it is capable of responding to optimization queries, like maximizing the output of a product given a set of input resources.
This tool uses [Z3](https://github.com/z3prover/z3), a powerful SMT solver to plan and optimize factories.

## Installation

0: Ensure that you have Python 3 installed, along with Z3 (including the python API) and the commentjson package

1: Download repository

2: Extract and run

## satisfactory-optimizer.py

	usage: satisfactory-optimizer.py [-h] [--items-file ITEMS_FILE_NAME] [--machines-file MACHINES_FILE_NAME] [--recipes-file RECIPES_FILE_NAME] [--precision PRECISION] problem_file_name

	A Satisfactory planner/optimizer based on Z3

	positional arguments:
	  problem_file_name     The location of the file containing the problem description.

	options:
	  -h, --help            show this help message and exit
	  --items-file ITEMS_FILE_NAME
	                        The location of the file containing item data (default: items.json).
	  --machines-file MACHINES_FILE_NAME
	                        The location of the file containing machine data (default: machines.json).
	  --recipes-file RECIPES_FILE_NAME
	                        The location of the file containing recipe data (default: recipes.json).
	  --precision PRECISION
	                        Specifies the number of digits to display after the decimal point when reporting fractional results (default: 2). Set to a negative number to display fractional values as exact fractions.

This is the main script file.
It takes a file listing the items, a file listing the machines, a file describing all of the available recipes, and a file describing the optimmization problem that you would like it to solve, and produces a factory plan.
All file input and output is formatted as JSON, with the extension that single-line comments are allowed.

The items, machines, and recipes are provided inside of the reposity, and generally don't need to be spacified unless you want to use a different set of recipes.
The recipes provided are for U6.

## problem-file

The problem file is where you specify what you'd like your factory to do.
You decide what recipes to use, what resources are available, and what constraints on the production graph you'd like to be satisfied.
You can also specify some optimization parameters as well.
The solver minimizes the power consumption of all factories once all other constraints are satisfied.

`test.json` is a problem file included in the repository which may be viewed as an example.

The problem description is broken up into several fields.
Each field is documented separately below.

### "included_recipes": ["Recipe OR Group", ...]

In order to plan a factory, some recipes must be enabled.
By default, no recipes are enabled.
Any recipes you want to use must be listed here.
Recipes are specified as a list of strings.

For the most part, the recipe names are the same as they are in-game.  The exceptions are:

 * "Alternate: Alclad Casing" -> "Alclad Casing"
 * "Electrode - Aluminum Scrap" -> "Electrode Aluminum Scrap"
 * "Turbo Rifle Ammo" -> "Pckaged Turbo Rifle Ammo" (For the recipe that uses the manufacturer)

There are also some additional recipes to be aware of that help plan factories.

 * "Extract Water"

   This recipe allows for water to be produced from nothing by way of water extractors.
   This is useful when you want to account for the power cost of water extractors in your factory.

 * "Burn [Fuel Item]"

   This recipe exists for every fuel item in the game that is consumed by a Biomass Burner, a Coal Generator, or a Fuel Generator.
   They provide negative power consumption to the factory, and can help with planning power plants.
   Nuclear Power Plants have their own recipes.

 * "Uranium Waste" and "Plutonium Waste"

   These are the recipes for nuclear power plants.
   Like the above recipes, they provide negative power consumption.
   They also have material outputs, as nuclear power plants produce waste.

 * "Sink [Item]"

   For every item that has a sink value, this recipe exists and can be used to plan factories that generate awesome sink points.

In addition to specifying recipes directly by name, they can also be specified in groups.
The recipe groups are also defined in the recipes file.
The groups in the file provided in this repo are "default", "alternate", "production", "ficsmas", "power", "sink_production", and "sink_ficsmas".

 * "default" contains all recipes in game which would be available to you after unlocking all of the milestones and completing all of the M.A.M. research.
   Note that this also contains the nuclear power plant recipes.
 * "alternate" contains all recipes which are unlocked by scanning hard drives.
 * "production" is equivalent to "default" + "alternate"
 * "ficsmas" contains all FICSMAS event recipes
 * "power" contains all "Burn [Fuel Item]" recipes, as well as the nuclear power plant recipes.
 * "sink_production" contains the sink recipes for all standard sinkable items.
 * "sink_ficsmas" contains the sink recipes for all FICSMAS event items.

### "excluded_recipes": ["Recipe OR Group", ...] (optional)

When specifying recipes in groups, it is sometimes useful to be able to exclude a handful of recipes from that group.
This field accepts the same set of values (including groups) as the "included_recipes" field does, but instead of enabling recipes, it disables them.
Disabling an already disabled recipe is not a problem.

### "input_items": {"Item": Real, ...}

A factory needs resources.
By default, the quantities of available items are all set to 0.
While there is a recipe that will allow the creation (really extraction) of water from nothing (but power), the other resources will need to be specified here.
Mining and other extraction recipes are not provided because of how irregular resource extraction is in this game.
The power cost of that process will have to be calculated and accounted for manually.

Input items are specified as a dictionary/object, with the item names as the keys, and the quantities as the values.
Any item may be specified, not just raw resources.
Quantities can be numbers, including decimals.
Quantities can also be strings containing numbers as decimals or fractions.
Because these values are interpreted by the Z3 library, they are treated as exact, and can have an arbitrary number of digits.
This is true of all locations where numbers may be specified.

Quantities here are all specified in units of items per minute.

There is also a special value which may be supplied in place of the quantity here: "unlimited".
This is useful for when you don't want to apply a particular upper bound to a resource, but want to supply it to the factory.

### "output_items": {"Item": Real, ...} (optional)

The format of this field is the same as for "input_items".
By default, the output quantities of all items are left unconstrained (or set to "unlimited").
Because of the minimization of power consumption, that means that the output factory plan won't produce anything unless it has to (unless you enable a power generation recipe, at which point it will try to plan a power plant with the available resources).

Setting a nonzero value here tells the factory planner that it should plan a factory that produces that item in the specified quantity.

Setting a zero value here has an interesting and sometimes useful effect.
Specifying that an item must _not_ be produced in this way constrains the planner such that any quantity of item which is produced must also be consumed by one or more recipes.
One place where this would be useful is when planning clean nuclear power.
Setting the output quantities of nuclear waste and its products to 0 forces the planner to account for the cost of processing it into plutonium fuel rods and sinking them, while not constraining which recipes it is allowed to use in doing so.

### "max_power_consumption": Real (optional)

If power consumption is a constraint, it may be specified.
Setting a value here constrains the planned factory to consume _at most_ the specified amount of power, in MW.
Negative values imply that the factory should produce _at least_ that much power.

### "optimization_goals": [["optimization_goal", *], ...] (optional)

This is where you specify parameters which you would like to maximize or minimize.
Each goal is a list with two parameters.
The first parameter is a string that specifies the type of optimization goal, and the second parameter .
The goal types and their behaviors are described below.

 * ["maximize_item_production", "Item"]

   Maximizes the number of the named item that is output by the factory (produced and not consumed).

 * ["minimize_item_production", "Item"]

   Minimizes the number of the named item that is output by the factory.
   This is useful for minimizing byproducts.

 * ["maximize_items_production", {"Item": Real, ...}]

   Maximizes the number of the named items that are output by the factory in the ratio specified by the quantities.
   For example, `"maximize_items_production": {"Iron Plate": 2, "Iron Rod": 1}` would maximize iron plate and iron rod production, but would maintain a 2:1 ratio between them.

 * ["maximize_item_consumption", "Item"]

   Maximizes the number of the named item that is _input_ by the factory (consumed but not produced).
   Mostly included for symmetry, but might be useful for pushing around which recipes are favored by the planner, though there are more direct ways to do that.

 * ["minimize_item_consumption", "Item"]

   Minimizes the number of the named item that is input by the factory.

 * ["maximize_item_flow", "Item"]

   Maximizes the number of the named item that is produced by the factory, but does not require that all of those items are outputs.
   This can be used to maximize the production of an item that is ultimately sinked, for example.

 * ["minimize_item_flow", "Item"]

   Minimizes the number of the named item that is produced by the factory, including internally.
   This could be used to push the factory away from using certain items that are difficult to transport like Screws, for example.

 * ["maximize_items_flow": {"Item": Real, ...}]

   The analog to "maximize_items_production", but like the other "flow" objectives, does not require that the items are all outputs of the factory.
   Useful for designing a factory that produces the Phase 4 project parts in the right ratios but ultimately sinks them, for example.

 * ["maximize_recipe": "Recipe"]

   Maxmizes the use of the named recipe.
   Can be useful for planning power plants.

 * ["minimize_recipe": "Recipe"]

   Minimizes the use of the named recipe.

Multiple goals may be specified.
Goals are applied in the order that they are specified.
This means that the factory is first optimized according to the first goal, and then the achieved consumption/flow/production is added as a hard constraint before optimizing according to the next goal, and so on.

After all listed goals are achieved, the factory is optimized for minimal power consumption.
This tends to cause the planner to plan power plants when power generation recipes are enabled and appropriate resources are available.
If you don't want to plan a power plant, don't enable power generation recipes.

This is one special item that is noteworthy here: "Awesome Sink Point".
It is not an item in the traditional sense, but it is the output of all of the "Sink [Item]" recipes.
It is possible to attempt to maximize or minimize the production of Awesome Sink points by naming this item in a maximization goal.

## items-file: ["Item", ...]

The contents of the items file is simply a list of strings, where each string is the name of an item.

## machines-file: ["Machine", ...]

The contents of the machines file is simply a list of strings, where each string is the name of a machine.

## recipes-file: {"Recipe": {*}, ...}

The contents of the recipes file is a dictionary/object, where the keys are the recipe names, and the values are the recipe objects.
Each recipe object has a number of fields which describe the recipe.

### "inputs": {"Item": Real, ...}

Specifies the inputs of the recipe.

### "outputs": {"Item": Real, ...}

Specifies the outputs of the recipe.

### "time": Real

Specifies how long the recipe takes to complete, in seconds.

### "machine": "Machine"

Specifies which machine is used to produce this recipe.

### "power_consumption": Real

Specifies the (average) power consumption of each machine in MW when producing this recipe.

### "tags": ["tag", ...] (optional)

Specifies which groups the recipe belongs to, for the purpose of making it easier to enable recipes in the problems file.
