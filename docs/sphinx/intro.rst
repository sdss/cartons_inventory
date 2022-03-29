
.. _intro:

Introduction to cartons_inventory
=================================

Cartons_inventory is a module crerated to retrieve targetdb information from a list of cartons.
These lists of cartons can come from rsconfig, a custom file, or a targetdb query.

The result can be a list of CartonInfo objects and/or a /csv file.

The main wrapper of this code is the method process_cartons which starts from a group of cartons
and first instantiates them as CartonInfo objects containing at creation only carton dependent
information (i.e. parameters that are the same for all targets from a given carton).
Then, one of its main pursposes it to use the method assign_target_info to assign target
dependent information for each carton (i.e. paramters that can differ for different stars from
the same carton). These parameters can be sets/ranges describing all the different values found
for cadence_pk, cadence_label, lambda_eff, instrument_pk, and instrument label along with the
minimum and maximum values of priority and value, or it can be the magnitude placeholders used
for each photometric system in that carton to indicate photometry was not valid for a given band.

This code can be used to create an input file acceptable by process_cartons from a targetdb query,
check the existence of a list of cartons, assign target dependent information for a group of
cartons, visualize the content of cartons, getting a dataframe with all the targets from a
carton, and saving the information from a group of cartons in a .csv file.


