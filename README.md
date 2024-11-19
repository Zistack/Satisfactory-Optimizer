# Satisfactory Optimizer

A simple command-line utility for planning factories in Satisfactory.
In addition to being a full replacement for online calculators (albeit with a less convenient user interface), it is capable of responding to optimization queries, like maximizing the output of a product given a set of input resources.
This tool uses [scipy.optimize.linprog](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html) to plan and optimize factories.

## Installation

0: Ensure that you have Python 3 installed, along with scipy and the commentjson package

1: Download repository

2: Extract and run

## satisfactory-optimizer.py

	usage: satisfactory-optimizer.py [-h] [--items-file ITEMS_FILE_NAME] [--machines-file MACHINES_FILE_NAME] [--recipes-file RECIPES_FILE_NAME] [--precision PRECISION] problem_file_name

	A Satisfactory planner/optimizer based on scipy.linprog.optimize

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
It takes a file listing the items, a file listing the machines, a file describing all of the available recipes, and a file describing the optimization problem that you would like it to solve, and produces a factory plan.
All file input and output is formatted as JSON, with the extension that single-line comments are allowed.

The items, machines, and recipes are provided inside of the repository, and generally don't need to be specified unless you want to use a different set of recipes.
The recipes provided are for the 1.0 release of the game.

## problem-file: {*}

The problem file is where you specify what you'd like your factory to do.
You decide what recipes to use, what resources are available, and what constraints on the production graph you'd like to be satisfied.
You can also specify some optimization parameters as well.
The solver minimizes the power consumption of all factories once all other constraints are satisfied.

Some example problems may be found in the `examples` directory of this repository.

 * `test.json` describes a factory that produces 60 reinforced iron plates per minute using only default recipes
 * `fuel_power` describes a fuel power plant that extracts as much power as is possible from 2 pure oil nodes using alternate recipes
 * `nitric_acid.json` describes a factory that produces as much nitric acid as is possible from the nitrogen gas well in the rocky desert.
 * `clean_nuclear.json` describes a power-maximized waste-free nuclear power setup.
 * `employee_of_the_universe.json` describes a factory that exploits all of the resources on the map to produce as many of the phase 4 project parts as is possible in the correct ratios.
 * `the_big_cheese.json` describes a factory that exploits all of the resources on the map to produce as many awesome sink points as is possible.

The problem description is broken up into several fields.
Each field is documented separately below.

### "included_recipes": ["Recipe OR Group", ...]

In order to plan a factory, some recipes must be enabled.
By default, no recipes are enabled.
Any recipes you want to use must be listed here.
Recipes are specified as a list of strings.

For the most part, the recipe names are the same as they are in-game, except that all alternate recipes have had their "Alternate: " prefix stripped from their name.
Besides that, The exceptions are:

 * "Electrode - Aluminum Scrap" -> "Electrode Aluminum Scrap"
 * "Turbo Rifle Ammo" -> "Packaged Turbo Rifle Ammo" (For the recipe that uses the manufacturer)

There are also some additional recipes to be aware of that help plan factories.

 * "Extract Water"

   This recipe allows for water to be produced from nothing by way of water extractors.
   This is useful when you want to account for the power cost of water extractors in your factory.

 * "Burn [Fuel Item]"

   This recipe exists for every fuel item in the game that is consumed by a Biomass Burner, a Coal Generator, or a Fuel Generator.  It also exists for Ficsonium fuel rods in a Nuclear Power Plant.
   They provide negative power consumption to the factory, and can help with planning power plants.
   Nuclear Power Plants have their own recipes.

 * "Uranium Waste" and "Plutonium Waste"

   These are recipes for nuclear power plants.
   Like the above recipes, they provide negative power consumption.
   They also have material outputs, as nuclear power plants produce waste.

 * "Sink [Item]"

   For every item that has a sink value, this recipe exists and can be used to plan factories that generate awesome sink points.
   These recipes assume that the awesome sink is fed by a mk.6 belt.

In addition to specifying recipes directly by name, they can also be specified in groups.
The recipe groups are also defined in the recipes file.
The groups in the file provided in this repo are as follows.

 * "miner_mkX" contains all recipes that use the Miner Mk.X (where X is 1, 2, or 3).
 * "oil_extractor" contains all recipes for the Oil Extractor.
 * "well_pressurizer" contains all recipes for the Resource Well Pressurizer.
 * "extraction" contains all of the above recipes as well as the "Extract Water" recipe for the Water Extractor.
 * "default" contains all recipes in game which would be available to you after unlocking all of the milestones and completing all of the M.A.M. research.
   Note that this also contains the nuclear power plant recipes.
 * "alternate" contains all recipes which are unlocked by scanning hard drives.
 * "production" is equivalent to "default" + "alternate".
 * "ficsmas" contains all FICSMAS event recipes.
 * "power" contains all "Burn [Fuel Item]" recipes, as well as the nuclear power plant recipes.
 * "sink_production" contains the sink recipes for all standard sinkable items.
 * "sink_ficsmas" contains the sink recipes for all FICSMAS event items.
 * "biomass_burner" contains all recipes for the Biomass Burner.
 * "coal_generator" contains all recipes for the Coal Generator.
 * "fuel_generator" contains all recipes for the Fuel Generator.
 * "geothermal_generator" contains all recipes for the Geothermal Generator.
 * "nuclear_power_plant" contains all recipes for the Nuclear Power Plant.
 * "power" contains all recipes that generate power.

There are also groups for all of the recipe categories defined by the game.  These groups are:

 * "standard_parts"
 * "electronics"
 * "compounds"
 * "biomass"
 * "alien_remains"
 * "power_shards"
 * "space_elevator"
 * "communications"
 * "industrial_parts"
 * "containers"
 * "nuclear"
 * "tools"
 * "ammunition"
 * "packaging" is notable because it contains all recipes for packing fluids into containers
 * "unpackaging" is similarly notable because it contains all recipes for unpacking fluids from containers
 * "oil_products"
 * "advanced_refinement"
 * "fuel"
 * "ingots"
 * "quantum_technology"
 * "raw_resource_conversion" is notable because it contains all raw resource transmutation recipes

### "excluded_recipes": ["Recipe OR Group", ...] (optional)

When specifying recipes in groups, it is sometimes useful to be able to exclude a handful of recipes from that group.
This field accepts the same set of values (including groups) as the "included_recipes" field does, but instead of enabling recipes, it disables them.
Disabling an already disabled recipe is not a problem.

### "nodes": {"Node Type": Int, ...} (optional)

If the factory will extract its own resources, then resource nodes may be specified.
The node types file defines Impure, Normal, and Pure versions of all node types.
Resource nodes are specified by their resource (sans the word 'Ore'), followed by the word 'Node'.
Examples: "Impure Iron Node", "Normal Uranium Node", "Pure Raw Quartz Node".
Geysers are also specified as "Impure/Normal/Pure Geyser".

### "wells": [...]

Resource wells may also be specified.
Each well is a dictionary with the following fields

#### "type": "Well Type"

The type field identifies the type of well, which ultimately dictates the recipes that may be used to extract resources from the well.

#### "satellites": {"Purity": Int, ...}

The satellites field lists the purities and counts of the available satellites surrounding the central pressurization point.

#### "count": Int (optional)

The count field specifies the number of wells with this configuration.
Defaults to 1.
Unless planning factories for a modded game, it is unlikely that this field will ever be needed.

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
This is true of all locations where numbers may be specified.

Quantities here are all specified in units of items per minute.

There is also a special value which may be supplied in place of the quantity here: "unlimited".
This is useful for when you don't want to apply a particular upper bound to a resource, but want to supply it to the factory.

### "output_items": {"Item": Real, ...} (optional)

The format of this field is the same as for "input_items".
By default, the output quantities of all items are left unconstrained (or set to "unlimited").
Because of the minimization of power consumption, that means that the output factory plan won't produce anything unless it has to (unless you enable a power generation recipe, at which point it will try to plan a power plant with the available resources).

By default, the factory planner assumes that no item may be output by the factory.
Setting a nonzero value here tells the factory planner that it should plan a factory that produces that item in the specified quantity.

Setting the special value "unlimited" here tells the planner that the resource may be output in any quantity.
This is useful for things like byproducts for factories with fixed outputs, or for outputs which you intend to maximize using optimization goals.
Not taking care to ensure that a factory can output (by)products can easily result in a factory plan which is either infeasible (in the case of a requested fixed output rate), or empty (in the case of output product maximization).

### "overclocking": {"Recipe OR Group": ...} (optional)

The factory planner supports overclocking, including for power generator recipes.
The recipe field acts much like the field for including or excluding recipes, in that groups may be specified as well as individual recipes.
Clock speeds are specified as a multiplier rather than a percentage, so the range of valid values is 0.01 - 2.5.
Values outside of that range will be clamped into that range.
The value set should be a dictionary/object with at least one of the following fields.

 * "min_clock_speed"

   The minimum clock speed allowed for this recipe.  Defaults to 1.

 * "max_clock_speed"

   The maximum clock speed allowed for this recipe.  Defaults to 1.

### "max_power_consumption": Real (optional)

If power consumption is a constraint, it may be specified.
Setting a value here constrains the planned factory to consume _at most_ the specified amount of power, in MW.
Negative values imply that the factory should produce _at least_ that much power.

### "available_somersloops": Integer (optional)

The factory planner can also optimize the allocation of somersloops to recipes for productivity boosts.
It would also be able to weigh this against using somersloops to build machines required for certain recipes, but in vanilla Satisfactory the only machine that requires somersloops to build is the Alien Power Augmenter, which provides a power augmentation factor, making it ineligible for machine count search (more in this in the next section).

Simply specify the number of somersloops that you are willing to dedicate to the factory, and the planner will try to determine the best place for them.

Note that productivity boosts and overclocking are often synergistic, so it is a good idea to allow the planner to overclock your production recipes when trying to optimize somersloop allocation.

Also note that, should any power augmentation recipes require somersloops in the construction of their machines, those must be made available for that construction here as well.
In other words, you are specifying the total number of somersloops that you are willing to allocate to this factory for any purpose, including power augmentation buildings.  Any somersloops not used in power augmentation buildings _may_ be allocated to boost the productivity of various recipes.

### "power_augmentation": {"Recipe": Real, ...} (optional)

Power augmentation recipes are a bit special.
The factory planner cannot reason about a variable power augmentation factor, because that would make the problem nonlinear.
If you want to use power augmentation in your factory, then you must manually specify how many machines you would like to dedicate to each recipe.
There are only two power augmentation recipes available:

 * "Alien Power Augmenter (Passive)" provides 500MW of power and a 10% power generation boost, tying up 10 somersloops and consuming no resources.
 * "Alien Power Augmenter (Active)" is like the above, but provides a 30% power generation boost, and consumes 5 Alien Power Matrix per minute.

Note that a sufficient quantity of somersloops must be made available via the "available_somersloops" field in order for the problem to have a solution.

### "max_machine_count": Real (optional)

For planning extremely large factories, it can be nice to put an upper bound on building count, as game performance becomes a concern.
Setting a value here constrains the planned factory to use _at most_ this many buildings.
Note that the planner operates on units of fractional buildings, so the actual number of buildings required to implement the output factory may be somewhat larger than the number given.

### "minimize_machine_count": Bool (optional)

If you would like to minimize machine count rather than minimizing power consumption, set this field to 'true'.
The field defaults to 'false'.
This will prevent the planner from maximizing power production on its own, so if this is used when designing a power plant, make sure to maximize the flow of whatever item is being used as fuel, and enable/disable the appropriate recipes.

### "optimization_goals": [["optimization_goal", *], ...] (optional)

This is where you specify parameters which you would like to maximize or minimize.
Each goal is a list with two parameters.
The first parameter is a string that specifies the type of optimization goal, and the type of the second parameter is determined by the type of goal.
The goal types and their behaviors are described below.

 * ["maximize_item_production", "Item"]

   Maximizes the number of the named item that is produced by any recipe (these items may be consumed).

 * ["minimize_item_production", "Item"]

   Minimizes the number of the named item that is produced by any recipe.
   This could be used to push the factory away from using certain items that are difficult to transport, like Screws, for example.

 * ["maximize_item_consumption", "Item"]

   Maximizes the number of the named item that is consumed by any recipe (these items may be produced).
   Mostly included for symmetry, but might be useful for pushing around which recipes are favored by the planner, though there are more direct ways to do that.

 * ["minimize_item_consumption", "Item"]

   Minimizes the number of the named item that is consumed by any recipe.

 * ["maximize_item_input", "Item"]

   Maximizes the number of the named item that is input by the factory (consumed or output but not produced).

 * ["minimize_item_input", "Item"]

   Minimizes the number of the named item that is input by the factory.

 * ["maximize_item_output", "Item"]

   Maximizes the number of the named item that is output by the factory (produced or input but not consumed)
   This can be used to maximize the production of an item that is ultimately sunk, for example.

 * ["minimize_item_output", "Item"]

   Minimizes the number of the named item that is output by the factory.
   This is useful for minimizing byproducts.

 * ["maximize_items_output", {"Item": Real, ...}]

   Maximizes the number of the named items that are output (produced or input but not consumed) by the factory in the ratio specified by the quantities.
   For example, `"maximize_items_production": {"Iron Plate": 2, "Iron Rod": 1}` would maximize iron plate and iron rod production, but would maintain a 2:1 ratio between them.

 * ["maximize_recipe", "Recipe OR Group"]

   This maximizes the number of machines used for a specific recipe or group of recipes.
   Groups are the same as those defined in the recipes file.
   Useful for constraining resource extraction or power generation, specifically.

   When a recipe group is specified, the actual objective function is simply the sum of the machine counts times their clock speeds.

 * ["minimize_recipe", "Recipe OR Group"]

   Like maximization above, but minimizes instead.

Multiple goals may be specified.
Goals are applied in the order that they are specified.
This means that the factory is first optimized according to the first goal, and then the achieved consumption/flow/production is added as a hard constraint before optimizing according to the next goal, and so on.

After all listed goals are achieved, the factory is optimized for minimal power consumption.
This tends to cause the planner to plan power plants when power generation recipes are enabled and appropriate resources are available.
If you don't want to plan a power plant, don't enable power generation recipes.

This is one special item that is noteworthy here: "Awesome Sink Point".
It is not an item in the traditional sense, but it is the output of all of the "Sink [Item]" recipes.
It is possible to attempt to maximize or minimize the production of Awesome Sink points by naming this item in an optimization goal.

## Output Format: {*}

Once the script is run, it will produce some output.
Assuming that there are no syntax errors or runtime bugs, it will either produce a factory plan, or it will say 'No solution found' in the case that the problem specification is over-constrained.

The factory plan is reported as a JSON dictionary/object with several entries.

### "items": {"Item": {*}, ...}

The "items" entry reports the number per minute of each item that passes through the factory, be that as in input, an output, an intermediate product, or some combination thereof.
Only items that actually appear in the factory plan with nonzero flows are reported.

 * "produced_by": {"Recipe": Real, ...}

   The amount of the item produced by each recipe is listed here for convenience.

 * "consumed_by": {"Recipe": Real, ...}

   The recipes which consume the item and the amount consumed by each is listed here.

### "machines": {"Machine": Real, ...}

The "machines" entry reports the number of each type of machine that is used in the factory.
As it is the sum of potentially fractional values, and a single machine cannot be used for more than one recipe, this is really a lower bound on the actual number of machines that you will have to build.
It can still be used to get an idea of how the production is distributed.

### "recipes": {"Recipe": {*}, ...}

The "recipes" entry reports some statistics about each recipe that is used in the factory plan.
Each recipe object contains the following entries:

 * "configurations": [...]

   Each configuration object describes a set of machines with a particular configuration (clock speed setting and number of somersloops slotted per machine).

   The "machine_count" field reports the number of machines that use the configuration.

   The "clock_speed_setting" reports the clock speed that all machines should be set to, if the machine supports overclocking.
   The optimizer underclocks all machines uniformly when a fractional number of machines would have been required.

   The "somersloops_slotted_per_machine" reports what it says it reports.
   If this field is not present, then that means that no somersloops should be slotted for this set of machines.

 * "power consumption": Real

   The approximate power consumption of all of the machines used to produce this recipe.
   This is an over-estimate due to the fact that the solver can't fully account for the non-linear effect on power consumption caused by changing the clock speed of a machine.

 * "inputs": {"Item": Real, ...}

   The number of items consumed by this recipe per minute for each item consumed.

 * "outputs": {"Item": Real, ...}

   The number of items produced by this recipe per minute for each item produced.

### "power_augmentation_recipes": {"Recipe": {*}, ...}

The "power_augmentation_recipes" entry reports recipe statistics for the power augmentation recipes that were manually specified in the problem description.
The format is the same, except for an additional field:

 * "total_power_augmentation_factor": Real

   The _total_ power augmentation factor contributed by all machines using this recipe.

### "power_consumption": Real

The "power_consumption" entry reports the total power consumption of machines which require power, in MW.
This ignores any power generated inside the factory.

### "power_production": Real

The "power_production" entry reports the total power generated by power generators, in MW.
This ignores any power needed for production machines. This field is only present if the factory includes machines which generate power.

### "augmented_power_production": Real

The "augmented_power_production" entry reports the total power generated, augmented by any connected power augmenters.
This field is only present if power augmentation is configured.

### "net_power_consumption": Real

The "net_power_consumption" entry reports the total power consumption of the entire factory, in MW.
Negative values imply that the factory actually _generates_ power.
This field is only present if the factory includes machines which generate power.

### "total_machine_count": Real

The "total_machine_count" entry reports the total number of machines used in the factory plan.
The same caveats about the use of fractional machines for the "machines" entry applies here as well.

# Appendix

## nodes-types-file: ["Node Type", ...]

The contents of the node types file is a list of strings, where each string identifies a type of node.

## well-types-file: ["Well Type", ...]

The contents of the well types file is a list of strings, where each string identifies a type of well.

## items-file: ["Item", ...]

The contents of the items file is a list of strings, where each string identifies a type of item.

## machines-file: {"Machine": {*}, ...}

The contents of the machines file is a dictionary.
The string keys name the types of machine.
The values are objects that can set properties of each machine.
These properties are:

 * "overclock_exponent": Real (optional)

   The presence of this field indicates that the machine supports overclocking and specifies the exponent associated with the power consumption modifier.

 * "somersloop_slots": Real (optional)

   The presence of this field indicates that the machine supports productivity boosting and specifies how many somersloops are required to achieve the maximum (2x) productivity bonus.

 * "required_somersloops": Real (optional)

   This field indicates how many somersloops are required to build the machine.
   The default value is 0.

## recipes-file: {"Recipe": {*}, ...}

The contents of the recipes file is a dictionary/object, where the keys are the recipe names, and the values are the recipe objects.
Each recipe object has a number of fields which describe the recipe.

### "node_type": "Node Type" (optional)

For node extraction recipes, this specifies the node type that the recipe may be used upon.
This field is mutually exclusive with "well_type".

### "well_type": "Well Type" (optional)

For well extraction recipes, this specifies the well type that the recipe may be used upon.
This field is mutually exclusive with "node_type".

### "resource": "Resource"

For well extraction recipes, this specifies the resource produced by the recipe.
This is only compatible with recipes that specify the "well_type" fields.
This must be specified for well recipes.

### "purity_quantities": {"Purity": Real}

For well extraction recipes, this specifies the production quantity per satellite of the given purity.
The output rate (in items per second) would be calculated by dividing this quantity by the value of the "time" field.
This must be specified for well recipes.

### "inputs": {"Item": Real, ...} (optional)

Specifies the inputs of the recipe.

### "outputs": {"Item": Real, ...} (optional)

Specifies the outputs of the recipe.
For recipes that specify a "well_type" field, this should not include the resource output from the satellite nodes.
For that purpose, the "resource" and "rate" or "purity_quantities" fields must be used.

### "time": Real

Specifies how long the recipe takes to complete, in seconds.

### "machine": "Machine"

Specifies which machine is used to produce this recipe.

### "power_consumption": Real

Specifies the (average) power consumption of each machine in MW when producing this recipe.
A negative power consumption implies that the recipe generates power.

### "power_augmentation_factor": Real

Specifies the power augmentation bonus provided by each machine using this recipe.
The presence of a power augmentation factor makes the recipe a power augmentation recipe, and so it becomes ineligible for optimization.
Power augmentation recipes must be requested manually in the problem description.

### "tags": ["tag", ...] (optional)

Specifies which groups the recipe belongs to, for the purpose of making it easier to enable/disable recipes in the problems file.
