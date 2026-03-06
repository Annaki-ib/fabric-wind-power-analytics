[StagingDefinition = [Kind = "FastCopy"]]
section Section1;
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "wind_power_DataDestination", IsNewTarget = false], Settings = [Kind = "Manual", AllowCreation = false, ColumnSettings = [Mappings = {[SourceColumnName = "production_id", DestinationColumnName = "production_id"], [SourceColumnName = "date", DestinationColumnName = "date"], [SourceColumnName = "turbine_name", DestinationColumnName = "turbine_name"], [SourceColumnName = "capacity", DestinationColumnName = "capacity"], [SourceColumnName = "location_name", DestinationColumnName = "location_name"], [SourceColumnName = "latitude", DestinationColumnName = "latitude"], [SourceColumnName = "longitude", DestinationColumnName = "longitude"], [SourceColumnName = "region", DestinationColumnName = "region"], [SourceColumnName = "status", DestinationColumnName = "status"], [SourceColumnName = "responsible_department", DestinationColumnName = "responsible_department"], [SourceColumnName = "wind_direction", DestinationColumnName = "wind_direction"], [SourceColumnName = "wind_speed", DestinationColumnName = "wind_speed"], [SourceColumnName = "energy_produced", DestinationColumnName = "energy_produced"], [SourceColumnName = "day", DestinationColumnName = "day"], [SourceColumnName = "month", DestinationColumnName = "month"], [SourceColumnName = "quarter", DestinationColumnName = "quarter"], [SourceColumnName = "year", DestinationColumnName = "year"], [SourceColumnName = "time", DestinationColumnName = "time"], [SourceColumnName = "hour_of_day", DestinationColumnName = "hour_of_day"], [SourceColumnName = "minute_of_hour", DestinationColumnName = "minute_of_hour"], [SourceColumnName = "second_of_minute", DestinationColumnName = "second_of_minute"], [SourceColumnName = "time_period", DestinationColumnName = "time_period"]}], DynamicSchema = false, UpdateMethod = [Kind = "Replace"], TypeSettings = [Kind = "Table"]]]}]
shared wind_power = let
  Source = Lakehouse.Contents(null),
  Navigation = Source{[workspaceId = "f6af98c0-78cd-4c2c-980e-b223713812d8"]}[Data],
  #"Navigation 1" = Navigation{[lakehouseId = "0393f8aa-610b-4250-a94b-ea5f48cc53c6"]}[Data],
  #"Navigation 2" = #"Navigation 1"{[Id = "wind_power", ItemKind = "Table"]}[Data],
  #"Rounded off" = Table.TransformColumns(#"Navigation 2", {{"energy_produced", each Number.Round(_, 2), type number}, {"wind_speed", each Number.Round(_, 2), type number}}),
  #"Inserted day" = Table.AddColumn(#"Rounded off", "Day", each Date.Day([date]), type nullable number),
  #"Inserted month" = Table.AddColumn(#"Inserted day", "Month", each Date.Month([date]), type nullable number),
  #"Inserted quarter" = Table.AddColumn(#"Inserted month", "Quarter", each Date.QuarterOfYear([date]), type nullable number),
  #"Inserted year" = Table.AddColumn(#"Inserted quarter", "Year", each Date.Year([date]), type nullable number),
  #"Changed column type" = Table.TransformColumnTypes(#"Inserted year", {{"Day", Int64.Type}, {"Month", Int64.Type}, {"Quarter", Int64.Type}, {"Year", Int64.Type}}),
  #"Renamed columns" = Table.RenameColumns(#"Changed column type", {{"Day", "day"}, {"Month", "month"}, {"Quarter", "quarter"}, {"Year", "year"}}),
  #"Replaced value" = Table.ReplaceValue(#"Renamed columns", "-", ":", Replacer.ReplaceText, {"time"}),
  #"Duplicated column" = Table.DuplicateColumn(#"Replaced value", "time", "time - Copy"),
  #"Split column by delimiter" = Table.SplitColumn(#"Duplicated column", "time - Copy", Splitter.SplitTextByDelimiter(":"), {"time - Copy.1", "time - Copy.2", "time - Copy.3"}),
  #"Changed column type 1" = Table.TransformColumnTypes(#"Split column by delimiter", {{"time - Copy.1", Int64.Type}, {"time - Copy.2", Int64.Type}, {"time - Copy.3", Int64.Type}}),
  #"Renamed columns 1" = Table.RenameColumns(#"Changed column type 1", {{"time - Copy.1", "hour_of_day"}, {"time - Copy.2", "minute_of_hour"}, {"time - Copy.3", "second_of_minute"}}),
  #"Added custom" = Table.TransformColumnTypes(Table.AddColumn(#"Renamed columns 1", "time_period", each if [hour_of_day] >= 5 and [hour_of_day] < 12 then "Morning"
else if [hour_of_day] >= 12 and [hour_of_day] < 17 then "Afternoon"
else if [hour_of_day] >= 17 and [hour_of_day] < 21 then "Evening"
else "Night"), {{"time_period", type text}})
in
  #"Added custom";
shared wind_power_DataDestination = let
  Pattern = Lakehouse.Contents([HierarchicalNavigation = null, CreateNavigationProperties = false, EnableFolding = false]),
  Navigation_1 = Pattern{[workspaceId = "f6af98c0-78cd-4c2c-980e-b223713812d8"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "485070a6-d495-48fc-93f3-713d62e6c282"]}[Data],
  TableNavigation = Navigation_2{[Id = "wind_power", ItemKind = "Table"]}[Data]
in
  TableNavigation;
