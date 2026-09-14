%% plot_6dof_plant_observer.m
% Plots the six degrees of freedom for the real plant and observer.
%
% Expected CSV headings:
%
%   time
%   x,     y,     z,     roll,     pitch,     yaw
%   xobs,  yobs,  zobs,  rollobs,  pitchobs,  yawobs
%
% All plant and observer signals use the same time vector.

clear;
clc;
close all;

%% ------------------------------------------------------------
% USER SETTINGS
% -------------------------------------------------------------

csvFile = "flight_data.csv";

% Set these according to the units in the CSV.
plantAnglesInRadians = false;
observerAnglesInRadians = false;

% Set to true to create an additional observer-error figure.
plotObserverErrors = true;

%% ------------------------------------------------------------
% CSV COLUMN NAMES
% -------------------------------------------------------------

columns.time = "time";

% Real plant columns
columns.x = "x";
columns.y = "y";
columns.z = "z";
columns.roll = "roll";
columns.pitch = "pitch";
columns.yaw = "yaw";

% Observer columns
columns.xobs = "x obs";
columns.yobs = "y obs";
columns.zobs = "z obs";
columns.rollobs = "roll obs";
columns.pitchobs = "pitch obs";
columns.yawobs = "yaw obs";

%% ------------------------------------------------------------
% IMPORT CSV FILE
% -------------------------------------------------------------

data = readtable( ...
    csvFile, ...
    "VariableNamingRule", "preserve");

fprintf("Loaded data from: %s\n", csvFile);
fprintf("Number of samples: %d\n", height(data));

%% ------------------------------------------------------------
% CHECK REQUIRED COLUMNS
% -------------------------------------------------------------

requiredColumns = [
    columns.time
    columns.x
    columns.y
    columns.z
    columns.roll
    columns.pitch
    columns.yaw
    columns.xobs
    columns.yobs
    columns.zobs
    columns.rollobs
    columns.pitchobs
    columns.yawobs
];

availableColumns = string(data.Properties.VariableNames);

missingColumns = requiredColumns( ...
    ~ismember(requiredColumns, availableColumns));

if ~isempty(missingColumns)
    fprintf("\nAvailable CSV columns:\n");
    disp(availableColumns');

    error( ...
        "The following required columns are missing: %s", ...
        strjoin(missingColumns, ", "));
end

%% ------------------------------------------------------------
% EXTRACT TIME
% -------------------------------------------------------------

time = double(data.(columns.time));
time = time(:);

% Remove the absolute starting time so that the plot begins at zero.
time = time - time(1);

%% ------------------------------------------------------------
% EXTRACT REAL PLANT DATA
% -------------------------------------------------------------

plant = struct();

plant.x = double(data.(columns.x));
plant.y = double(data.(columns.y));
plant.z = double(data.(columns.z));

plant.roll = double(data.(columns.roll));
plant.pitch = double(data.(columns.pitch));
plant.yaw = double(data.(columns.yaw));

%% ------------------------------------------------------------
% EXTRACT OBSERVER DATA
% -------------------------------------------------------------

observer = struct();

observer.x = double(data.(columns.xobs));
observer.y = double(data.(columns.yobs));
observer.z = double(data.(columns.zobs));

observer.roll = double(data.(columns.rollobs));
observer.pitch = double(data.(columns.pitchobs));
observer.yaw = double(data.(columns.yawobs));

%% ------------------------------------------------------------
% CONVERT ANGLES TO DEGREES IF REQUIRED
% -------------------------------------------------------------

if plantAnglesInRadians
    plant.roll = rad2deg(plant.roll);
    plant.pitch = rad2deg(plant.pitch);
    plant.yaw = rad2deg(plant.yaw);
end

if observerAnglesInRadians
    observer.roll = rad2deg(observer.roll);
    observer.pitch = rad2deg(observer.pitch);
    observer.yaw = rad2deg(observer.yaw);
end

%% ------------------------------------------------------------
% REMOVE ROWS CONTAINING INVALID DATA
% -------------------------------------------------------------

validRows = isfinite(time);

stateNames = [
    "x"
    "y"
    "z"
    "roll"
    "pitch"
    "yaw"
];

for stateName = stateNames'
    validRows = validRows ...
        & isfinite(plant.(stateName)) ...
        & isfinite(observer.(stateName));
end

time = time(validRows);

for stateName = stateNames'
    plant.(stateName) = plant.(stateName)(validRows);
    observer.(stateName) = observer.(stateName)(validRows);
end

%% ------------------------------------------------------------
% SORT DATA BY TIME
% -------------------------------------------------------------

[time, sortIndex] = sort(time);

for stateName = stateNames'
    plant.(stateName) = plant.(stateName)(sortIndex);
    observer.(stateName) = observer.(stateName)(sortIndex);
end

%% ------------------------------------------------------------
% PLOT ALL SIX DEGREES OF FREEDOM
% -------------------------------------------------------------

figure( ...
    "Name", "Plant and Observer 6DOF Comparison", ...
    "Color", "w");

plotLayout = tiledlayout(3, 2);

plotLayout.TileSpacing = "compact";
plotLayout.Padding = "compact";

title( ...
    plotLayout, ...
    "Real Plant and Observer: 6DOF Comparison");

% X position
nexttile;

plotStateComparison( ...
    time, ...
    plant.x, ...
    observer.x, ...
    "X Position", ...
    "Position (m)");

% Y position
nexttile;

plotStateComparison( ...
    time, ...
    plant.y, ...
    observer.y, ...
    "Y Position", ...
    "Position (m)");

% Z position
nexttile;

plotStateComparison( ...
    time, ...
    plant.z, ...
    observer.z, ...
    "Z Position", ...
    "Position (m)");

% Roll
nexttile;

plotStateComparison( ...
    time, ...
    plant.roll, ...
    observer.roll, ...
    "Roll", ...
    "Angle (deg)");

% Pitch
nexttile;

plotStateComparison( ...
    time, ...
    plant.pitch, ...
    observer.pitch, ...
    "Pitch", ...
    "Angle (deg)");

% Yaw
nexttile;

plotStateComparison( ...
    time, ...
    plant.yaw, ...
    observer.yaw, ...
    "Yaw", ...
    "Angle (deg)");

%% ------------------------------------------------------------
% CALCULATE OBSERVER ERRORS
% -------------------------------------------------------------

errorData = struct();
rmseValues = zeros(numel(stateNames), 1);

for index = 1:numel(stateNames)
    stateName = stateNames(index);

    errorData.(stateName) = ...
        plant.(stateName) - observer.(stateName);

    rmseValues(index) = sqrt( ...
        mean(errorData.(stateName).^2));
end

%% ------------------------------------------------------------
% DISPLAY RMSE RESULTS
% -------------------------------------------------------------

fprintf("\nObserver RMSE\n");
fprintf("--------------------------------\n");
fprintf("X position: %+.5f m\n", rmseValues(1));
fprintf("Y position: %+.5f m\n", rmseValues(2));
fprintf("Z position: %+.5f m\n", rmseValues(3));
fprintf("Roll:       %+.5f deg\n", rmseValues(4));
fprintf("Pitch:      %+.5f deg\n", rmseValues(5));
fprintf("Yaw:        %+.5f deg\n", rmseValues(6));

%% ------------------------------------------------------------
% OPTIONAL OBSERVER-ERROR PLOTS
% -------------------------------------------------------------

if plotObserverErrors

    figure( ...
        "Name", "6DOF Observer Errors", ...
        "Color", "w");

    errorLayout = tiledlayout(3, 2);

    errorLayout.TileSpacing = "compact";
    errorLayout.Padding = "compact";

    title( ...
        errorLayout, ...
        "Real Plant Minus Observer");

    stateTitles = [
        "X Position Error"
        "Y Position Error"
        "Z Position Error"
        "Roll Error"
        "Pitch Error"
        "Yaw Error"
    ];

    stateUnits = [
        "Error (m)"
        "Error (m)"
        "Error (m)"
        "Error (deg)"
        "Error (deg)"
        "Error (deg)"
    ];

    for index = 1:numel(stateNames)
        stateName = stateNames(index);

        nexttile;

        plot( ...
            time, ...
            errorData.(stateName), ...
            "k", ...
            "LineWidth", 1.2, ...
            "DisplayName", "Estimation error");

        hold on;

        yline( ...
            0, ...
            "--", ...
            "Zero error", ...
            "Color", [0.5, 0.5, 0.5]);

        grid on;
        box on;

        title(stateTitles(index));
        xlabel("Time (s)");
        ylabel(stateUnits(index));

        xlim([time(1), time(end)]);
    end
end

%% ------------------------------------------------------------
% LOCAL FUNCTION
% -------------------------------------------------------------

function plotStateComparison( ...
    time, ...
    plantState, ...
    observerState, ...
    plotTitle, ...
    yAxisLabel)

    plot( ...
        time, ...
        plantState, ...
        "r", ...
        "LineWidth", 1.5, ...
        "DisplayName", "Real plant");

    hold on;

    plot( ...
        time, ...
        observerState, ...
        "b--", ...
        "LineWidth", 1.5, ...
        "DisplayName", "Observer");

    grid on;
    box on;

    title(plotTitle);
    xlabel("Time (s)");
    ylabel(yAxisLabel);

    xlim([time(1), time(end)]);

    legend( ...
        "Location", ...
        "best");
end