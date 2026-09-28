clear;
clc;
close all;

%% ============================================================
%% PID vs Pole-Placement Altitude Ramp Response Comparison
%% Written for Jonah Habel, 2026
%% ============================================================

%% ==========================
%% Settings
%% ==========================
numRuns = 5;

% Adjust these patterns if the CSV filenames differ.
% The %d is replaced by the run number from 1 to numRuns.
PID_FILE_PATTERN = 'PID_Test_result_%d.csv';
PP_FILE_PATTERN  = 'PP_Test_result_%d.csv';

% CSV column headers
COLS.time           = "time";
COLS.altitude       = "z";
COLS.targetAltitude = "target altitude (m)";

% Set true to reset the first recorded sample to t = 0 s.
RESET_TIME_TO_ZERO = true;

% Plot formatting
AXIS_FONT_SIZE   = 20;
LEGEND_FONT_SIZE = 18;
TICK_FONT_SIZE   = 16;
TITLE_FONT_SIZE  = 26;

% Individual-run colours are lighter versions of the mean colours.
PID_RUN_COLOUR  = [0.55 0.75 1.00];   % Light blue
PID_MEAN_COLOUR = [0.00 0.25 0.90];   % Bold blue

PP_RUN_COLOUR   = [1.00 0.68 0.55];   % Light orange/red
PP_MEAN_COLOUR  = [0.90 0.20 0.05];   % Bold orange/red

TARGET_COLOUR = [0.00 0.00 0.00];

INDIVIDUAL_LINE_WIDTH = 1.0;
MEAN_LINE_WIDTH       = 3.0;
TARGET_LINE_WIDTH     = 2.2;

%% ==========================
%% Load Controller Data
%% ==========================
[pidRuns, pidTargets, pidTimes] = loadControllerRuns( ...
    PID_FILE_PATTERN, numRuns, COLS);

[ppRuns, ppTargets, ppTimes] = loadControllerRuns( ...
    PP_FILE_PATTERN, numRuns, COLS);

%% ==========================
%% Determine Common Time Base
%% ==========================
% Each recorded run may contain a slightly different number of samples or
% slightly different timestamps. Interpolate all runs onto one common time
% vector so that pointwise means are valid.

commonStartTime = max([ ...
    cellfun(@(x) x(1), pidTimes), ...
    cellfun(@(x) x(1), ppTimes)]);

commonEndTime = min([ ...
    cellfun(@(x) x(end), pidTimes), ...
    cellfun(@(x) x(end), ppTimes)]);

allSampleIntervals = [];

for k = 1:numRuns
    allSampleIntervals = [ ...
        allSampleIntervals; ...
        diff(pidTimes{k}); ...
        diff(ppTimes{k})]; %#ok<AGROW>
end

allSampleIntervals = allSampleIntervals( ...
    isfinite(allSampleIntervals) & allSampleIntervals > 0);

if isempty(allSampleIntervals)
    error('Unable to determine a valid sample interval from the CSV files.');
end

commonDt = median(allSampleIntervals);
time = (commonStartTime:commonDt:commonEndTime).';

if length(time) < 2
    error('The PID and pole-placement recordings do not share enough common time data.');
end

%% ==========================
%% Interpolate All Runs
%% ==========================
pidAltitude = nan(length(time), numRuns);
ppAltitude  = nan(length(time), numRuns);

pidTarget = nan(length(time), numRuns);
ppTarget  = nan(length(time), numRuns);

for k = 1:numRuns
    pidAltitude(:,k) = interp1( ...
        pidTimes{k}, pidRuns{k}, time, 'linear');

    ppAltitude(:,k) = interp1( ...
        ppTimes{k}, ppRuns{k}, time, 'linear');

    pidTarget(:,k) = interp1( ...
        pidTimes{k}, pidTargets{k}, time, 'linear');

    ppTarget(:,k) = interp1( ...
        ppTimes{k}, ppTargets{k}, time, 'linear');
end

if RESET_TIME_TO_ZERO
    time = time - time(1);
end

%% ==========================
%% Convert Altitude to cm
%% ==========================
pidAltitudeCm = pidAltitude .* 100;
ppAltitudeCm  = ppAltitude  .* 100;

pidTargetCm = pidTarget .* 100;
ppTargetCm  = ppTarget  .* 100;

%% ==========================
%% Calculate Statistics
%% ==========================
meanPidAltitudeCm = mean(pidAltitudeCm, 2, 'omitnan');
meanPpAltitudeCm  = mean(ppAltitudeCm,  2, 'omitnan');

% Use the mean target across all ten recordings. This remains robust to
% very small timestamp or floating-point differences between CSV files.
targetAltitudeCm = mean( ...
    [pidTargetCm, ppTargetCm], 2, 'omitnan');

pidErrorCm = pidTargetCm - pidAltitudeCm;
ppErrorCm  = ppTargetCm  - ppAltitudeCm;

pidRmseCm = sqrt(mean(pidErrorCm.^2, 1, 'omitnan'));
ppRmseCm  = sqrt(mean(ppErrorCm.^2,  1, 'omitnan'));

pidMaeCm = mean(abs(pidErrorCm), 1, 'omitnan');
ppMaeCm  = mean(abs(ppErrorCm),  1, 'omitnan');

fprintf('\n============================================================\n');
fprintf('PID vs Pole-Placement Ramp Response Summary\n');
fprintf('============================================================\n');
fprintf('Common duration: %.3f s\n', time(end) - time(1));
fprintf('Common sample interval: %.6f s\n\n', commonDt);

for k = 1:numRuns
    fprintf( ...
        'PID Run %d | RMSE = %7.3f cm | MAE = %7.3f cm\n', ...
        k, pidRmseCm(k), pidMaeCm(k));
end

fprintf('\n');

for k = 1:numRuns
    fprintf( ...
        'PP  Run %d | RMSE = %7.3f cm | MAE = %7.3f cm\n', ...
        k, ppRmseCm(k), ppMaeCm(k));
end

fprintf('\n');
fprintf( ...
    'PID overall | Mean RMSE = %.3f cm | Mean MAE = %.3f cm\n', ...
    mean(pidRmseCm, 'omitnan'), mean(pidMaeCm, 'omitnan'));

fprintf( ...
    'PP overall  | Mean RMSE = %.3f cm | Mean MAE = %.3f cm\n', ...
    mean(ppRmseCm, 'omitnan'), mean(ppMaeCm, 'omitnan'));
fprintf('============================================================\n\n');

%% ==========================
%% Plot Ramp Responses
%% ==========================
figure( ...
    'Color', 'w', ...
    'Position', [100 100 1400 760]);

hold on;

% % Plot faint PID trials.
% for k = 1:numRuns
%     if k == 1
%         plot( ...
%             time, pidAltitudeCm(:,k), ...
%             'Color', PID_RUN_COLOUR, ...
%             'LineWidth', INDIVIDUAL_LINE_WIDTH, ...
%             'DisplayName', 'PID Individual Runs');
%     else
%         plot( ...
%             time, pidAltitudeCm(:,k), ...
%             'Color', PID_RUN_COLOUR, ...
%             'LineWidth', INDIVIDUAL_LINE_WIDTH, ...
%             'HandleVisibility', 'off');
%     end
% end
% 
% % Plot faint pole-placement trials.
% for k = 1:numRuns
%     if k == 1
%         plot( ...
%             time, ppAltitudeCm(:,k), ...
%             'Color', PP_RUN_COLOUR, ...
%             'LineWidth', INDIVIDUAL_LINE_WIDTH, ...
%             'DisplayName', 'Pole-Placement Individual Runs');
%     else
%         plot( ...
%             time, ppAltitudeCm(:,k), ...
%             'Color', PP_RUN_COLOUR, ...
%             'LineWidth', INDIVIDUAL_LINE_WIDTH, ...
%             'HandleVisibility', 'off');
%     end
% end

% Plot bold controller means.
plot( ...
    time, meanPidAltitudeCm, ...
    'Color', PID_MEAN_COLOUR, ...
    'LineWidth', MEAN_LINE_WIDTH, ...
    'DisplayName', 'Mean PID Altitude');

plot( ...
    time, meanPpAltitudeCm, ...
    'Color', PP_MEAN_COLOUR, ...
    'LineWidth', MEAN_LINE_WIDTH, ...
    'DisplayName', 'Mean Pole-Placement Altitude');

% Plot common target profile last so it remains visible.
plot( ...
    time, targetAltitudeCm, ...
    'Color', TARGET_COLOUR, ...
    'LineStyle', '--', ...
    'LineWidth', TARGET_LINE_WIDTH, ...
    'DisplayName', 'Target Altitude');

xlabel('Time (s)', 'FontSize', AXIS_FONT_SIZE);
ylabel('Altitude (cm)', 'FontSize', AXIS_FONT_SIZE);
title( ...
    'PID and Pole-Placement Altitude Ramp Responses', ...
    'FontWeight', 'bold', ...
    'FontSize', TITLE_FONT_SIZE);

set(gca, 'FontSize', TICK_FONT_SIZE);
grid on;
box on;
xlim([time(1), time(end)]);

legend( ...
    'Location', 'eastoutside', ...
    'FontSize', LEGEND_FONT_SIZE);

%% ==========================
%% Local Function
%% ==========================
function [altitudeRuns, targetRuns, timeRuns] = loadControllerRuns( ...
    filePattern, numRuns, COLS)

    altitudeRuns = cell(1, numRuns);
    targetRuns   = cell(1, numRuns);
    timeRuns     = cell(1, numRuns);

    requiredCols = [ ...
        COLS.time, ...
        COLS.altitude, ...
        COLS.targetAltitude];

    for runNumber = 1:numRuns
        filename = sprintf(filePattern, runNumber);

        if ~isfile(filename)
            error('CSV file not found: %s', filename);
        end

        data = readtable( ...
            filename, ...
            'VariableNamingRule', 'preserve');

        availableCols = string(data.Properties.VariableNames);
        missingCols = requiredCols(~ismember(requiredCols, availableCols));

        if ~isempty(missingCols)
            error( ...
                'Missing columns in %s: %s', ...
                filename, ...
                strjoin(cellstr(missingCols), ', '));
        end

        runTime = double(data.(COLS.time));
        runAltitude = double(data.(COLS.altitude));
        runTarget = double(data.(COLS.targetAltitude));

        validRows = ...
            isfinite(runTime) ...
            & isfinite(runAltitude) ...
            & isfinite(runTarget);

        runTime     = runTime(validRows);
        runAltitude = runAltitude(validRows);
        runTarget   = runTarget(validRows);

        if length(runTime) < 2
            error('Insufficient valid data in %s.', filename);
        end

        % Remove duplicate timestamps because interp1 requires unique input
        % values. The stable option retains the original sample order.
        [runTime, uniqueIndices] = unique(runTime, 'stable');
        runAltitude = runAltitude(uniqueIndices);
        runTarget   = runTarget(uniqueIndices);

        % Ensure time is increasing even if the CSV rows were unordered.
        [runTime, sortIndices] = sort(runTime);
        runAltitude = runAltitude(sortIndices);
        runTarget   = runTarget(sortIndices);

        timeRuns{runNumber}     = runTime;
        altitudeRuns{runNumber} = runAltitude;
        targetRuns{runNumber}   = runTarget;

        fprintf( ...
            'Loaded %-30s | %6d valid samples\n', ...
            filename, length(runTime));
    end
end
