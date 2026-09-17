%% observer_6dof_validation.m
% Written by Jonah Habel 2026
% Flinders University
%
% Validates plant and observer 6DOF data stored in one CSV file.
%
% Requirements:
%   Position error: +/-0.005 m
%   Attitude error: +/-0.2 deg
%   A continuous exceedance lasting more than 0.5 s is a failure.
%
% Required CSV headings:
%   time, x, y, z, roll, pitch, yaw,
%   x obs, y obs, z obs, roll obs, pitch obs, yaw obs

clear;
clc;
close all;

%% USER SETTINGS
csvFile = "flight_data.csv";

figureHeading = "Observer 6DOF Error vs Time";
testDescription = "Jonah Habel - Observer Validation";

plantAnglesInRadians = false;
observerAnglesInRadians = false;

% ==========================
% Requirements
% ==========================

XYPositionErrorLimit = 10;    % cm
AltitudeErrorLimit   = 4;     % cm

RollErrorLimit  = 0.5;        % deg
PitchErrorLimit = 0.5;        % deg
YawErrorLimit   = 0.3;        % deg

maximumExceedanceDuration = 1.5;   % s

showFailureShading = true;
showExceedanceMarkers = false;
showResultTextBoxes = true;

resultsFile = "observer_validation_results.csv";
eventResultsFile = "observer_exceedance_events.csv";
figureFile = "observer_6dof_error_validation.png";
matlabFigureFile = "observer_6dof_error_validation.fig";

%% CSV COLUMN NAMES
columns.time = "time";
columns.x = "x";
columns.y = "y";
columns.z = "z";
columns.roll = "roll";
columns.pitch = "pitch";
columns.yaw = "yaw";
columns.xobs = "x obs";
columns.yobs = "y obs";
columns.zobs = "z obs";
columns.rollobs = "roll obs";
columns.pitchobs = "pitch obs";
columns.yawobs = "yaw obs";

%% STATE DEFINITIONS
stateNames = ["x"; "y"; "z"; "roll"; "pitch"; "yaw"];

observerColumnNames = [ ...
    "x obs";
    "y obs";
    "z obs";
    "roll obs";
    "pitch obs";
    "yaw obs"];

stateTitles = [ ...
    "X Position Error";
    "Y Position Error";
    "Altitude Error";
    "Roll Error";
    "Pitch Error";
    "Yaw Error"];

stateUnits = [ ...
    "cm";
    "cm";
    "cm";
    "deg";
    "deg";
    "deg"];

requirementLimits = [ ...
    XYPositionErrorLimit;
    XYPositionErrorLimit;
    AltitudeErrorLimit;
    RollErrorLimit;
    PitchErrorLimit;
    YawErrorLimit];

numberOfStates = numel(stateNames);

angleStates = ["roll"; "pitch"; "yaw"];
positionStates = ["x"; "y"; "z"];

%% IMPORT CSV
if ~isfile(csvFile)
    error('CSV file not found: %s', char(csvFile));
end

data = readtable(csvFile, "VariableNamingRule", "preserve");
fprintf('Loaded CSV file: %s\n', char(csvFile));
fprintf('Imported rows: %d\n', height(data));

%% CHECK REQUIRED COLUMNS
requiredColumns = [columns.time; columns.x; columns.y; columns.z; ...
    columns.roll; columns.pitch; columns.yaw; columns.xobs; ...
    columns.yobs; columns.zobs; columns.rollobs; columns.pitchobs; ...
    columns.yawobs];
availableColumns = string(data.Properties.VariableNames);
missingColumns = requiredColumns(~ismember(requiredColumns, availableColumns));

if ~isempty(missingColumns)
    fprintf('\nAvailable CSV columns:\n');
    disp(availableColumns');
    error('Missing required CSV columns: %s', ...
        char(strjoin(missingColumns, ", ")));
end

%% EXTRACT DATA
time = double(data.(columns.time));
time = time(:);

plant = struct();
plant.x = double(data.(columns.x));
plant.y = double(data.(columns.y));
plant.z = double(data.(columns.z));
plant.roll = double(data.(columns.roll));
plant.pitch = double(data.(columns.pitch));
plant.yaw = double(data.(columns.yaw));

observer = struct();
observer.x = double(data.(columns.xobs));
observer.y = double(data.(columns.yobs));
observer.z = double(data.(columns.zobs));
observer.roll = double(data.(columns.rollobs));
observer.pitch = double(data.(columns.pitchobs));
observer.yaw = double(data.(columns.yawobs));

for stateIndex = 1:numberOfStates
    stateName = char(stateNames(stateIndex));
    plant.(stateName) = plant.(stateName)(:);
    observer.(stateName) = observer.(stateName)(:);
end

%% CONVERT ANGLES TO DEGREES IF REQUIRED
if plantAnglesInRadians
    for stateIndex = 1:numel(angleStates)
        stateName = char(angleStates(stateIndex));
        plant.(stateName) = rad2deg(plant.(stateName));
    end
end

if observerAnglesInRadians
    for stateIndex = 1:numel(angleStates)
        stateName = char(angleStates(stateIndex));
        observer.(stateName) = rad2deg(observer.(stateName));
    end
end

%% CONVERT POSITIONS TO CM

for stateIndex = 1:numel(positionStates)

    stateName = char(positionStates(stateIndex));

    plant.(stateName) = plant.(stateName) .* 100;
    observer.(stateName) = observer.(stateName) .* 100;

end

%% REMOVE INVALID ROWS
validRows = isfinite(time);
for stateIndex = 1:numberOfStates
    stateName = char(stateNames(stateIndex));
    validRows = validRows & isfinite(plant.(stateName)) ...
        & isfinite(observer.(stateName));
end

numberOfRemovedRows = sum(~validRows);
time = time(validRows);
for stateIndex = 1:numberOfStates
    stateName = char(stateNames(stateIndex));
    plant.(stateName) = plant.(stateName)(validRows);
    observer.(stateName) = observer.(stateName)(validRows);
end

fprintf('Removed invalid rows: %d\n', numberOfRemovedRows);
fprintf('Valid rows remaining: %d\n', numel(time));
if numel(time) < 2
    error('At least two valid samples are required.');
end

%% SORT AND REMOVE DUPLICATE TIMES
[time, sortIndex] = sort(time);
for stateIndex = 1:numberOfStates
    stateName = char(stateNames(stateIndex));
    plant.(stateName) = plant.(stateName)(sortIndex);
    observer.(stateName) = observer.(stateName)(sortIndex);
end

[time, uniqueTimeIndex] = unique(time, "stable");
for stateIndex = 1:numberOfStates
    stateName = char(stateNames(stateIndex));
    plant.(stateName) = plant.(stateName)(uniqueTimeIndex);
    observer.(stateName) = observer.(stateName)(uniqueTimeIndex);
end

if numel(time) < 2
    error('At least two unique time samples are required.');
end

%% NORMALISE TIME
time = time - time(1);
timeDifferences = diff(time);
positiveTimeDifferences = timeDifferences(timeDifferences > 0);
if isempty(positiveTimeDifferences)
    error('The time column does not contain increasing values.');
end

medianSampleTime = median(positiveTimeDifferences);
approximateSampleRate = 1 / medianSampleTime;
fprintf('Test duration: %.3f s\n', time(end));
fprintf('Median sample time: %.6f s\n', medianSampleTime);
fprintf('Approximate sample rate: %.2f Hz\n', approximateSampleRate);

%% CALCULATE ERRORS AND EXCEEDANCE EVENTS
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
    stateNameString = stateNames(stateIndex);
    stateName = char(stateNameString);
    errorLimit = requirementLimits(stateIndex);

    signedError = plant.(stateName) - observer.(stateName);
    if any(stateNameString == angleStates)
        signedError = mod(signedError + 180, 360) - 180;
    end

    absoluteError = abs(signedError);
    signedErrors.(stateName) = signedError;
    absoluteErrors.(stateName) = absoluteError;
    maximumAbsoluteError(stateIndex) = max(absoluteError);
    meanAbsoluteError(stateIndex) = mean(absoluteError);
    rootMeanSquareError(stateIndex) = sqrt(mean(signedError .^ 2));

    exceeded = absoluteError > errorLimit;
    exceedanceMasks.(stateName) = exceeded;
    percentageWithinLimit(stateIndex) = 100 * mean(~exceeded);

    transitions = diff([false; exceeded; false]);
    runStarts = find(transitions == 1);
    runEnds = find(transitions == -1) - 1;
    numberOfExceedanceEvents(stateIndex) = numel(runStarts);

    durations = zeros(numel(runStarts), 1);
    peakErrors = zeros(numel(runStarts), 1);
    failedSamples = false(size(exceeded));

    for eventIndex = 1:numel(runStarts)
        startIndex = runStarts(eventIndex);
        endIndex = runEnds(eventIndex);
        durations(eventIndex) = time(endIndex) - time(startIndex) ...
            + medianSampleTime;
        peakErrors(eventIndex) = max(absoluteError(startIndex:endIndex));

        if durations(eventIndex) > maximumExceedanceDuration
            failedSamples(startIndex:endIndex) = true;
        end
    end

    failedIntervalMasks.(stateName) = failedSamples;
    eventStartIndices{stateIndex} = runStarts;
    eventEndIndices{stateIndex} = runEnds;
    eventDurations{stateIndex} = durations;
    eventPeakErrors{stateIndex} = peakErrors;

    if isempty(durations)
        longestExceedanceDuration(stateIndex) = 0;
    else
        longestExceedanceDuration(stateIndex) = max(durations);
    end

    numberOfFailedEvents(stateIndex) = sum( ...
        durations > maximumExceedanceDuration);
    validationPassed(stateIndex) = numberOfFailedEvents(stateIndex) == 0;
end

%% CREATE VALIDATION RESULTS TABLE
resultText = strings(numberOfStates, 1);
for stateIndex = 1:numberOfStates
    if validationPassed(stateIndex)
        resultText(stateIndex) = "PASS";
    else
        resultText(stateIndex) = "FAIL";
    end
end

allowedDurationColumn = repmat( ...
    maximumExceedanceDuration, numberOfStates, 1);

validationResults = table(stateNames, observerColumnNames, stateUnits, ...
    requirementLimits, allowedDurationColumn, maximumAbsoluteError, ...
    meanAbsoluteError, rootMeanSquareError, longestExceedanceDuration, ...
    numberOfExceedanceEvents, numberOfFailedEvents, ...
    percentageWithinLimit, resultText, ...
    'VariableNames', {'State', 'ObserverColumn', 'Unit', 'ErrorLimit', ...
    'MaximumAllowedExceedance_s', 'MaximumAbsoluteError', ...
    'MeanAbsoluteError', 'RMSE', 'LongestExceedance_s', ...
    'ExceedanceEventCount', 'FailedEventCount', ...
    'PercentageWithinLimit', 'Result'});

fprintf('\nOBSERVER VALIDATION RESULTS\n');
fprintf('============================================================\n');
disp(validationResults);
writetable(validationResults, resultsFile);
fprintf('Validation results saved to: %s\n', char(resultsFile));

%% CREATE EXCEEDANCE EVENT TABLE
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
        eventStartTime(end + 1, 1) = time(runStarts(eventIndex));
        eventEndTime(end + 1, 1) = time(runEnds(eventIndex));
        continuousDuration(end + 1, 1) = durations(eventIndex);
        peakAbsoluteError(end + 1, 1) = peakErrors(eventIndex);
        eventLimit(end + 1, 1) = requirementLimits(stateIndex);

        if durations(eventIndex) > maximumExceedanceDuration
            eventResult(end + 1, 1) = "FAIL";
        else
            eventResult(end + 1, 1) = "PERMITTED";
        end
    end
end

exceedanceEventResults = table(eventState, eventNumber, eventStartTime, ...
    eventEndTime, continuousDuration, peakAbsoluteError, eventLimit, ...
    eventResult, 'VariableNames', {'State', 'EventNumber', ...
    'StartTime_s', 'EndTime_s', 'Duration_s', 'PeakAbsoluteError', ...
    'RequirementLimit', 'Result'});

writetable(exceedanceEventResults, eventResultsFile);
fprintf('Exceedance events saved to: %s\n', char(eventResultsFile));

%% DETERMINE OVERALL RESULT
overallPass = all(validationPassed);
if overallPass
    overallResultText = "PASS";
    overallResultColour = [0.00, 0.45, 0.00];
else
    overallResultText = "FAIL";
    overallResultColour = [0.80, 0.00, 0.00];
end

fprintf('\nOVERALL VALIDATION RESULT: %s\n', char(overallResultText));
fprintf('============================================================\n');

if overallPass
    fprintf(['No state exceeded its applicable error requirement ' ...
        'continuously for more than %.3f seconds.\n'], ...
        maximumExceedanceDuration);
else
    fprintf(['One or more states exceeded the applicable error ' ...
        'requirement continuously for more than %.3f seconds.\n'], ...
        maximumExceedanceDuration);
    fprintf('\nFailed states:\n');

    for stateIndex = 1:numberOfStates
        if ~validationPassed(stateIndex)
            fprintf('  %s: longest exceedance = %.3f s\n', ...
                char(stateNames(stateIndex)), ...
                longestExceedanceDuration(stateIndex));
        end
    end
end

%% CREATE PRESENTATION-STYLE VALIDATION FIGURE
figureHandle = figure("Name", "Observer 6DOF Error Validation", ...
    "Color", "w", "Position", [80, 40, 1400, 920]);

plotLayout = tiledlayout(3, 2);
plotLayout.TileSpacing = "compact";
plotLayout.Padding = "compact";

titleHandle = title(plotLayout, ...
    {char(figureHeading), char(testDescription)});
titleHandle.FontSize = 16;
titleHandle.FontWeight = "bold";

for stateIndex = 1:numberOfStates
    stateName = char(stateNames(stateIndex));
    errorLimit = requirementLimits(stateIndex);
    signedError = signedErrors.(stateName);
    exceeded = exceedanceMasks.(stateName);
    failedSamples = failedIntervalMasks.(stateName);

    nexttile;
    hold on;

    observedMaximum = max(abs(signedError));
    verticalLimit = max(1.5 * errorLimit, 1.10 * observedMaximum);

    if stateUnits(stateIndex) == "cm"
    
        verticalLimit = max(verticalLimit, ...
            1.5 * requirementLimits(stateIndex));
    
    else
    
        verticalLimit = max(verticalLimit, 0.75);
    
    end

    if showFailureShading && any(failedSamples)
        failedTransitions = diff([false; failedSamples; false]);
        failedStarts = find(failedTransitions == 1);
        failedEnds = find(failedTransitions == -1) - 1;

        for failureIndex = 1:numel(failedStarts)
            failureStartTime = time(failedStarts(failureIndex));
            failureEndTime = time(failedEnds(failureIndex));

            patch([failureStartTime, failureEndTime, failureEndTime, ...
                failureStartTime], [-verticalLimit, -verticalLimit, ...
                verticalLimit, verticalLimit], [1.00, 0.88, 0.88], ...
                "EdgeColor", "none", "FaceAlpha", 0.55, ...
                "HandleVisibility", "off");
        end
    end

    plot(time, signedError, "k", "LineWidth", 2.4, ...
        "DisplayName", "Observer Error");

    if showExceedanceMarkers && any(exceeded)
        scatter(time(exceeded), signedError(exceeded), 15, ...
            [0.85, 0.10, 0.10], "filled", ...
            "DisplayName", "Requirement Exceeded");
    end

    positiveLabel = sprintf('+%.4g %s Requirement', errorLimit, ...
        char(stateUnits(stateIndex)));
    negativeLabel = sprintf('-%.4g %s Requirement', errorLimit, ...
        char(stateUnits(stateIndex)));

    plot(time, errorLimit * ones(size(time)), "--", ...
        "Color", [1.00, 0.30, 0.30], "LineWidth", 2.0, ...
        "DisplayName", positiveLabel);
    plot(time, -errorLimit * ones(size(time)), "--", ...
        "Color", [1.00, 0.30, 0.30], "LineWidth", 2.0, ...
        "DisplayName", negativeLabel);

    yline(0, "-", "Color", [0.55, 0.55, 0.55], ...
        "LineWidth", 0.8, "HandleVisibility", "off");

    if validationPassed(stateIndex)
        stateResultColour = [0.00, 0.45, 0.00];
    else
        stateResultColour = [0.80, 0.00, 0.00];
    end

    subplotTitle = sprintf('%s - %s', char(stateTitles(stateIndex)), ...
        char(resultText(stateIndex)));
    title(subplotTitle, "FontWeight", "bold", "FontSize", 12, ...
        "Color", stateResultColour);
    xlabel("Time (s)", "FontSize", 11);

    if stateUnits(stateIndex) == "m"
        ylabel("Position Error (m)", "FontSize", 11);
    else
        ylabel("Attitude Error (deg)", "FontSize", 11);
    end

    xlim([time(1), time(end)]);
    ylim([-verticalLimit, verticalLimit]);
    grid on;
    box on;

    axesHandle = gca;
    axesHandle.FontSize = 10;
    axesHandle.LineWidth = 0.8;
    axesHandle.GridAlpha = 0.25;
    axesHandle.MinorGridAlpha = 0.15;
    axesHandle.Layer = "top";

    if showResultTextBoxes
        validationText = sprintf(['%s\nMaximum error: %.4g %s\n' ...
            'Longest exceedance: %.3f s\nPermitted duration: %.3f s'], ...
            char(resultText(stateIndex)), maximumAbsoluteError(stateIndex), ...
            char(stateUnits(stateIndex)), ...
            longestExceedanceDuration(stateIndex), ...
            maximumExceedanceDuration);

        text(0.02, 0.04, validationText, "Units", "normalized", ...
            "VerticalAlignment", "bottom", "FontSize", 8.5, ...
            "FontWeight", "bold", "Color", stateResultColour, ...
            "BackgroundColor", "w", "EdgeColor", [0.70, 0.70, 0.70], ...
            "Margin", 4);
    end

    legend("Location", "best", "FontSize", 8.5, "Box", "on");
end

%% ADD OVERALL RESULT TO FIGURE
overallAnnotation = sprintf( ...
    'OVERALL RESULT: %s | Maximum continuous exceedance permitted: 1.5 s', ...
    char(overallResultText));

annotation(figureHandle, "textbox", [0.29, 0.002, 0.42, 0.035], ...
    "String", overallAnnotation, "HorizontalAlignment", "center", ...
    "VerticalAlignment", "middle", "FontWeight", "bold", ...
    "FontSize", 11, "Color", overallResultColour, ...
    "EdgeColor", overallResultColour, "BackgroundColor", "w", ...
    "LineWidth", 1.2);

drawnow;

%% SAVE FIGURE
exportgraphics(figureHandle, figureFile, "Resolution", 300);
savefig(figureHandle, matlabFigureFile);
fprintf('\nSaved validation figure: %s\n', char(figureFile));
fprintf('Saved editable MATLAB figure: %s\n', char(matlabFigureFile));

%% PRINT EXCEEDANCE EVENTS
fprintf('\nCONTINUOUS REQUIREMENT EXCEEDANCE EVENTS\n');
fprintf('============================================================\n');

for stateIndex = 1:numberOfStates
    stateName = stateNames(stateIndex);
    runStarts = eventStartIndices{stateIndex};
    runEnds = eventEndIndices{stateIndex};
    durations = eventDurations{stateIndex};
    peakErrors = eventPeakErrors{stateIndex};

    fprintf('\n%s:\n', char(upper(stateName)));

    if isempty(durations)
        fprintf('  No requirement exceedances detected.\n');
        continue;
    end

    for eventIndex = 1:numel(durations)
        if durations(eventIndex) > maximumExceedanceDuration
            currentEventResult = "FAIL";
        else
            currentEventResult = "PERMITTED";
        end

        fprintf(['  Event %d: %.3f s to %.3f s, duration %.3f s, ' ...
            'peak error %.4g %s, %s\n'], eventIndex, ...
            time(runStarts(eventIndex)), time(runEnds(eventIndex)), ...
            durations(eventIndex), peakErrors(eventIndex), ...
            char(stateUnits(stateIndex)), char(currentEventResult));
    end
end

fprintf('\nValidation processing complete.\n');
