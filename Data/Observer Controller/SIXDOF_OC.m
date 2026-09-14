%% observer_6dof_validation.m
% Written by Jonah Habel 2026
% Flinders University
%
% Observer 6DOF validation using plant and observer data exported
% in the same CSV file.
%
% REQUIREMENTS
%
% Position estimation error:
%   |x - xobs| <= 0.005 m
%   |y - yobs| <= 0.005 m
%   |z - zobs| <= 0.005 m
%
% Attitude estimation error:
%   |roll  - rollobs|  <= 0.2 deg
%   |pitch - pitchobs| <= 0.2 deg
%   |yaw   - yawobs|   <= 0.2 deg
%
% Temporary exceedances are permitted, provided that the error does not
% continuously exceed the applicable limit for more than 0.5 seconds.
%
% EXPECTED CSV COLUMN HEADINGS
%
%   time
%   x, y, z
%   roll, pitch, yaw
%   xobs, yobs, zobs
%   rollobs, pitchobs, yawobs
%
% Plant and observer data must use the same time vector.

clear;
clc;
close all;

%% ============================================================
% USER SETTINGS
% =============================================================

csvFile = "flight_data.csv";

% Figure information
figureHeading = "Observer 6DOF Error vs Time";
testDescription = ...
    "Jonah Habel - Observer Validation - 14.09.2026";

% Set these to true if the corresponding CSV attitude values
% are stored in radians.
plantAnglesInRadians = false;
observerAnglesInRadians = false;

% Requirement limits
positionErrorLimit = 0.005;       % metres
attitudeErrorLimit = 0.2;         % degrees

% Maximum permitted continuous exceedance
maximumExceedanceDuration = 0.5;  % seconds

% Plot options
showFailureShading = true;
showExceedanceMarkers = false;
showResultTextBoxes = true;

% Output files
resultsFile = "observer_validation_results.csv";
eventResultsFile = "observer_exceedance_events.csv";
figureFile = "observer_6dof_error_validation.png";
matlabFigureFile = "observer_6dof_error_validation.fig";

%% ============================================================
% CSV COLUMN NAMES
% =============================================================

columns.time = "time";

% Plant columns
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

%% ============================================================
% STATE DEFINITIONS
% =============================================================

stateNames = [
    "x"
    "y"
    "z"
    "roll"
    "pitch"
    "yaw"
];

observerColumnNames = [
    "x obs"
    "y obs"
    "z obs"
    "roll obs"
    "pitch obs"
    "yaw obs"
];

stateTitles = [
    "X Position Error"
    "Y Position Error"
    "Z Position Error"
    "Roll Error"
    "Pitch Error"
    "Yaw Error"
];

stateUnits = [
    "m"
    "m"
    "m"
    "deg"
    "deg"
    "deg"
];

requirementLimits = [
    positionErrorLimit
    positionErrorLimit
    positionErrorLimit
    attitudeErrorLimit
    attitudeErrorLimit
    attitudeErrorLimit
];

numberOfStates = numel(stateNames);

%% ============================================================
% IMPORT CSV
% =============================================================

if ~isfile(csvFile)
    error("CSV file not found: %s", csvFile);
end

data = readtable( ...
    csvFile, ...
    "VariableNamingRule", "preserve");

fprintf("Loaded CSV file: %s\n", csvFile);
fprintf("Imported rows: %d\n", height(data));

%% ============================================================
% CHECK REQUIRED COLUMNS
% =============================================================

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
        "Missing required CSV columns: %s", ...
        strjoin(missingColumns, ", "));
end

%% ============================================================
% EXTRACT TIME
% =============================================================

time = double(data.(columns.time));
time = time(:);

%% ============================================================
% EXTRACT PLANT DATA
% =============================================================

plant = struct();

plant.x = double(data.(columns.x));
plant.y = double(data.(columns.y));
plant.z = double(data.(columns.z));

plant.roll = double(data.(columns.roll));
plant.pitch = double(data.(columns.pitch));
plant.yaw = double(data.(columns.yaw));

%% ============================================================
% EXTRACT OBSERVER DATA
% =============================================================

observer = struct();

observer.x = double(data.(columns.xobs));
observer.y = double(data.(columns.yobs));
observer.z = double(data.(columns.zobs));

observer.roll = double(data.(columns.rollobs));
observer.pitch = double(data.(columns.pitchobs));
observer.yaw = double(data.(columns.yawobs));

%% ============================================================
% ENSURE ALL SIGNALS ARE COLUMN VECTORS
% =============================================================

for stateIndex = 1:numberOfStates
    stateName = stateNames(stateIndex);

    plant.(stateName) = plant.(stateName)(:);
    observer.(stateName) = observer.(stateName)(:);
end

%% ============================================================
% CONVERT ATTITUDE TO DEGREES IF REQUIRED
% =============================================================

angleStates = [
    "roll"
    "pitch"
    "yaw"
];

if plantAnglesInRadians
    for stateIndex = 1:numel(angleStates)
        stateName = angleStates(stateIndex);

        plant.(stateName) = ...
            rad2deg(plant.(stateName));
    end
end

if observerAnglesInRadians
    for stateIndex = 1:numel(angleStates)
        stateName = angleStates(stateIndex);

        observer.(stateName) = ...
            rad2deg(observer.(stateName));
    end
end

%% ============================================================
% REMOVE INVALID ROWS
% =============================================================

validRows = isfinite(time);

for stateIndex = 1:numberOfStates
    stateName = stateNames(stateIndex);

    validRows = validRows ...
        & isfinite(plant.(stateName)) ...
        & isfinite(observer.(stateName));
end

numberOfRemovedRows = sum(~validRows);

time = time(validRows);

for stateIndex = 1:numberOfStates
    stateName = stateNames(stateIndex);

    plant.(stateName) = ...
        plant.(stateName)(validRows);

    observer.(stateName) = ...
        observer.(stateName)(validRows);
end

fprintf("Removed invalid rows: %d\n", numberOfRemovedRows);
fprintf("Valid rows remaining: %d\n", numel(time));

if numel(time) < 2
    error("At least two valid samples are required.");
end

%% ============================================================
% SORT DATA BY TIME
% =============================================================

[time, sortIndex] = sort(time);

for stateIndex = 1:numberOfStates
    stateName = stateNames(stateIndex);

    plant.(stateName) = ...
        plant.(stateName)(sortIndex);

    observer.(stateName) = ...
        observer.(stateName)(sortIndex);
end

%% ============================================================
% REMOVE DUPLICATE TIME VALUES
% =============================================================

[time, uniqueTimeIndex] = unique(time, "stable");

for stateIndex = 1:numberOfStates
    stateName = stateNames(stateIndex);

    plant.(stateName) = ...
        plant.(stateName)(uniqueTimeIndex);

    observer.(stateName) = ...
        observer.(stateName)(uniqueTimeIndex);
end

if numel(time) < 2
    error("At least two unique time samples are required.");
end

%% ============================================================
% NORMALISE TIME
% =============================================================

time = time - time(1);

timeDifferences = diff(time);

positiveTimeDifferences = ...
    timeDifferences(timeDifferences > 0);

if isempty(positiveTimeDifferences)
    error("The time column does not contain increasing values.");
end

medianSampleTime = median(positiveTimeDifferences);
approximateSampleRate = 1 / medianSampleTime;

fprintf("Test duration: %.3f s\n", time(end));
fprintf("Median sample time: %.6f s\n", medianSampleTime);
fprintf("Approximate sample rate: %.2f Hz\n", ...
    approximateSampleRate);

%% ============================================================
% CALCULATE SIGNED AND ABSOLUTE ERRORS
% =============================================================

signedErrors = struct();
absoluteErrors = struct();
exceedanceMasks = struct();
failedIntervalMasks = struct();

maximumAbsoluteError = zeros(numberOfStates, 1);
meanAbsoluteError = zeros(numberOfStates, 1);
rootMeanSquareError = zeros(numberOfStates, 1);
percentageWithinLimit = zeros(numberOfStates, 1);

longestExceedanceDuration = zeros(numberOfStates, 1);
numberOfExceedanceEvents = zeros(numberOfStates, 1);
numberOfFailedEvents = zeros(numberOfStates, 1);

validationPassed = false(numberOfStates, 1);

eventStartIndices = cell(numberOfStates, 1);
eventEndIndices = cell(numberOfStates, 1);
eventDurations = cell(numberOfStates, 1);
eventPeakErrors = cell(numberOfStates, 1);

for stateIndex = 1:numberOfStates

    stateName = stateNames(stateIndex);
    errorLimit = requirementLimits(stateIndex);

    % Plant minus observer
    signedError = ...
        plant.(stateName) - observer.(stateName);

    % Wrap attitude errors so that angular subtraction remains between
    % -180 degrees and +180 degrees.
    if any(stateName == angleStates)
        signedError = mod( ...
            signedError + 180, ...
            360) - 180;
    end

    absoluteError = abs(signedError);

    signedErrors.(stateName) = signedError;
    absoluteErrors.(stateName) = absoluteError;

    maximumAbsoluteError(stateIndex) = ...
        max(absoluteError);

    meanAbsoluteError(stateIndex) = ...
        mean(absoluteError);

    rootMeanSquareError(stateIndex) = ...
        sqrt(mean(signedError.^2));

    % True whenever the magnitude requirement is exceeded.
    exceeded = absoluteError > errorLimit;

    exceedanceMasks.(stateName) = exceeded;

    percentageWithinLimit(stateIndex) = ...
        100 * mean(~exceeded);

    %% Find continuous exceedance intervals

    transitions = diff([false; exceeded; false]);

    runStarts = find(transitions == 1);
    runEnds = find(transitions == -1) - 1;

    numberOfExceedanceEvents(stateIndex) = ...
        numel(runStarts);

    durations = zeros(numel(runStarts), 1);
    peakErrors = zeros(numel(runStarts), 1);

    failedSamples = false(size(exceeded));

    for eventIndex = 1:numel(runStarts)

        startIndex = runStarts(eventIndex);
        endIndex = runEnds(eventIndex);

        % Include approximately one sample interval. This represents
        % the time occupied by the final recorded sample in the event.
        durations(eventIndex) = ...
            time(endIndex) ...
            - time(startIndex) ...
            + medianSampleTime;

        peakErrors(eventIndex) = max( ...
            absoluteError(startIndex:endIndex));

        % The requirement allows an exceedance lasting up to and
        % including 0.5 seconds. A failure occurs only when the
        % continuous duration is greater than 0.5 seconds.
        if durations(eventIndex) > ...
                maximumExceedanceDuration

            failedSamples(startIndex:endIndex) = true;
        end
    end

    failedIntervalMasks.(stateName) = ...
        failedSamples;

    eventStartIndices{stateIndex} = runStarts;
    eventEndIndices{stateIndex} = runEnds;
    eventDurations{stateIndex} = durations;
    eventPeakErrors{stateIndex} = peakErrors;

    if isempty(durations)
        longestExceedanceDuration(stateIndex) = 0;
    else
        longestExceedanceDuration(stateIndex) = ...
            max(durations);
    end

    numberOfFailedEvents(stateIndex) = sum( ...
        durations > maximumExceedanceDuration);

    validationPassed(stateIndex) = ...
        numberOfFailedEvents(stateIndex) == 0;
end

%% ============================================================
% CREATE VALIDATION RESULTS TABLE
% =============================================================

resultText = strings(numberOfStates, 1);

for stateIndex = 1:numberOfStates
    if validationPassed(stateIndex)
        resultText(stateIndex) = "PASS";
    else
        resultText(stateIndex) = "FAIL";
    end
end

allowedExceedanceDurationColumn = repmat( ...
    maximumExceedanceDuration, ...
    numberOfStates, ...
    1);

validationResults = table( ...
    stateNames, ...
    observerColumnNames, ...
    stateUnits, ...
    requirementLimits, ...
    allowedExceedanceDurationColumn, ...
    maximumAbsoluteError, ...
    meanAbsoluteError, ...
    rootMeanSquareError, ...
    longestExceedanceDuration, ...
    numberOfExceedanceEvents, ...
    numberOfFailedEvents, ...
    percentageWithinLimit, ...
    resultText, ...
    'VariableNames', { ...
        'State', ...
        'ObserverColumn', ...
        'Unit', ...
        'ErrorLimit', ...
        'MaximumAllowedExceedance_s', ...
        'MaximumAbsoluteError', ...
        'MeanAbsoluteError', ...
        'RMSE', ...
        'LongestExceedance_s', ...
        'ExceedanceEventCount', ...
        'FailedEventCount', ...
        'PercentageWithinLimit', ...
        'Result' ...
    });

fprintf("\n");
fprintf("OBSERVER VALIDATION RESULTS\n");
fprintf("============================================================\n");
disp(validationResults);

writetable(validationResults, resultsFile);

fprintf("Validation results saved to:\n");
fprintf("  %s\n", resultsFile);

%% ============================================================
% CREATE EXCEEDANCE EVENT TABLE
% =============================================================

eventState = strings(0, 1);
eventNumber = zeros(0, 1);
eventStartTime = zeros(0, 1);
eventEndTime = zeros(0, 1);
continuousDuration = zeros(0, 1);
peakAbsoluteError = zeros(0, 1);
eventLimit = zeros(0, 1);
eventResult = strings(0, 1);

for stateIndex = 1:numberOfStates

    stateName = stateNames(stateIndex);

    runStarts = eventStartIndices{stateIndex};
    runEnds = eventEndIndices{stateIndex};
    durations = eventDurations{stateIndex};
    peakErrors = eventPeakErrors{stateIndex};

    for eventIndex = 1:numel(runStarts)

        eventState(end + 1, 1) = stateName;
        eventNumber(end + 1, 1) = eventIndex;

        eventStartTime(end + 1, 1) = ...
            time(runStarts(eventIndex));

        eventEndTime(end + 1, 1) = ...
            time(runEnds(eventIndex));

        continuousDuration(end + 1, 1) = ...
            durations(eventIndex);

        peakAbsoluteError(end + 1, 1) = ...
            peakErrors(eventIndex);

        eventLimit(end + 1, 1) = ...
            requirementLimits(stateIndex);

        if durations(eventIndex) > ...
                maximumExceedanceDuration

            eventResult(end + 1, 1) = "FAIL";
        else
            eventResult(end + 1, 1) = "PERMITTED";
        end
    end
end

exceedanceEventResults = table( ...
    eventState, ...
    eventNumber, ...
    eventStartTime, ...
    eventEndTime, ...
    continuousDuration, ...
    peakAbsoluteError, ...
    eventLimit, ...
    eventResult, ...
    'VariableNames', { ...
        'State', ...
        'EventNumber', ...
        'StartTime_s', ...
        'EndTime_s', ...
        'Duration_s', ...
        'PeakAbsoluteError', ...
        'RequirementLimit', ...
        'Result' ...
    });

writetable( ...
    exceedanceEventResults, ...
    eventResultsFile);

fprintf("Exceedance events saved to:\n");
fprintf("  %s\n", eventResultsFile);

%% ============================================================
% DETERMINE OVERALL RESULT
% =============================================================

overallPass = all(validationPassed);

if overallPass
    overallResultText = "PASS";
    overallResultColour = [0.00, 0.45, 0.00];
else
    overallResultText = "FAIL";
    overallResultColour = [0.80, 0.00, 0.00];
end

fprintf('\n');
fprintf( ...
    'OVERALL VALIDATION RESULT: %s\n', ...
    char(overallResultText));

fprintf( ...
    '============================================================\n');

if overallPass

    fprintf( ...
        ['No state exceeded its applicable error requirement ' ...
         'continuously for more than %.3f seconds.\n'], ...
        maximumExceedanceDuration);

else

    fprintf( ...
        ['One or more states exceeded the applicable error ' ...
         'requirement continuously for more than %.3f seconds.\n'], ...
        maximumExceedanceDuration);

    fprintf('\nFailed states:\n');

    for stateIndex = 1:numberOfStates

        if ~validationPassed(stateIndex)

            fprintf( ...
                '  %s: longest exceedance = %.3f s\n', ...
                char(stateNames(stateIndex)), ...
                longestExceedanceDuration(stateIndex));

        end
    end
end

%% ============================================================
% ADD OVERALL RESULT TO FIGURE
% =============================================================

overallAnnotation = sprintf( ...
    [ ...
        'OVERALL RESULT: %s     ' ...
        'Maximum continuous exceedance permitted: %.1f s' ...
    ], ...
    overallResultText, ...
    maximumExceedanceDuration);

annotation( ...
    figureHandle, ...
    "textbox", ...
    [0.29, 0.002, 0.42, 0.035], ...
    "String", overallAnnotation, ...
    "HorizontalAlignment", "center", ...
    "VerticalAlignment", "middle", ...
    "FontWeight", "bold", ...
    "FontSize", 11, ...
    "Color", overallResultColour, ...
    "EdgeColor", overallResultColour, ...
    "BackgroundColor", "w", ...
    "LineWidth", 1.2);

%% ============================================================
% SAVE FIGURE
% =============================================================

exportgraphics( ...
    figureHandle, ...
    figureFile, ...
    "Resolution", 300);

savefig( ...
    figureHandle, ...
    matlabFigureFile);

fprintf("\nSaved validation figure:\n");
fprintf("  %s\n", figureFile);

fprintf("Saved editable MATLAB figure:\n");
fprintf("  %s\n", matlabFigureFile);

%% ============================================================
% PRINT EXCEEDANCE EVENTS
% =============================================================

fprintf("\n");
fprintf("CONTINUOUS REQUIREMENT EXCEEDANCE EVENTS\n");
fprintf("============================================================\n");

for stateIndex = 1:numberOfStates

    stateName = stateNames(stateIndex);

    runStarts = eventStartIndices{stateIndex};
    runEnds = eventEndIndices{stateIndex};
    durations = eventDurations{stateIndex};
    peakErrors = eventPeakErrors{stateIndex};

    fprintf("\n%s:\n", upper(stateName));

    if isempty(durations)
        fprintf("  No requirement exceedances detected.\n");
        continue;
    end

    for eventIndex = 1:numel(durations)

        if durations(eventIndex) > ...
                maximumExceedanceDuration

            currentEventResult = "FAIL";
        else
            currentEventResult = "PERMITTED";
        end

        fprintf( ...
            [ ...
                "  Event %d: %.3f s to %.3f s, " ...
                "duration %.3f s, peak error %.4g %s, %s\n" ...
            ], ...
            eventIndex, ...
            time(runStarts(eventIndex)), ...
            time(runEnds(eventIndex)), ...
            durations(eventIndex), ...
            peakErrors(eventIndex), ...
            stateUnits(stateIndex), ...
            currentEventResult);
    end
end

fprintf("\nValidation processing complete.\n");