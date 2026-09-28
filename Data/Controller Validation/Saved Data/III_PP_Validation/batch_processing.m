clear;
clc;
close all;

%% ==========================
%% Settings
%% ==========================
numFiles = 10;

ATTITUDE_LIMIT_DEG = 2.25;
ALT_ERROR_LIMIT_CM = 18;
AXIS_FONT_SIZE = 20
LEGEND_FONT_SIZE = 18
TICK_FONT_SIZE = 16

% CSV column headers
COLS.time            = "time";
COLS.pitch           = "pitch";
COLS.roll            = "roll";
COLS.altitude        = "z";
COLS.targetAltitude  = "target altitude (m)";

%% ==========================
%% Find Shortest Run
%% ==========================
minLength = inf;

for k = 1:numFiles

    filename = sprintf('III_PP_Validation_result_%d.csv', k);

    data = readtable(filename, ...
        'VariableNamingRule','preserve');

    minLength = min(minLength, height(data));

end

fprintf('Shortest run length = %d samples\n', minLength);

%% ==========================
%% Preallocate
%% ==========================
pitch_all    = zeros(minLength,numFiles);
roll_all     = zeros(minLength,numFiles);
altitude_all = zeros(minLength,numFiles);

%% ==========================
%% Load Data
%% ==========================
for k = 1:numFiles

    filename = sprintf('III_PP_Validation_result_%d.csv', k);

    data = readtable(filename, ...
        'VariableNamingRule','preserve');

    %% Verify Required Columns Exist

    requiredCols = string(struct2cell(COLS));

    missingCols = requiredCols( ...
        ~ismember(requiredCols, ...
        string(data.Properties.VariableNames)));

    if ~isempty(missingCols)

        error(['Missing columns in ', filename, ': ', ...
            strjoin(cellstr(missingCols), ', ')]);

    end

    %% Extract Data

    pitch_all(:,k)    = data.(COLS.pitch)(1:minLength);
    roll_all(:,k)     = data.(COLS.roll)(1:minLength);
    altitude_all(:,k) = data.(COLS.altitude)(1:minLength);

    %% Use First Run As Reference

    if k == 1

        time = data.(COLS.time)(1:minLength);

        target_altitude = ...
            data.(COLS.targetAltitude)(1:minLength);

    end

end

%% ==========================
%% Statistics
%% ==========================
mean_pitch = mean(pitch_all,2);
mean_roll  = mean(roll_all,2);
mean_alt   = mean(altitude_all,2);

%% Convert Altitude to cm
altitude_all_cm    = altitude_all .* 100;
mean_alt_cm        = mean_alt .* 100;
target_altitude_cm = target_altitude .* 100;

mean_alt_error_cm = ...
    target_altitude_cm - mean_alt_cm;

%% ==========================
%% Diagnostics
%% ==========================
fprintf('\n------ Run Limits ------\n');

for k = 1:numFiles

    maxPitch = max(abs(pitch_all(:,k)));
    maxRoll  = max(abs(roll_all(:,k)));

    fprintf( ...
        'Run %02d | Max Pitch = %.3f deg | Max Roll = %.3f deg\n', ...
        k, maxPitch, maxRoll);

end

%% ==========================
%% Combined Figure
%% ==========================
figure( ...
    'Color','w', ...
    'Position',[100 100 1400 900]);

tiledlayout(3,1, ...
    'TileSpacing','compact', ...
    'Padding','compact');

%% ==========================
%% Attitude Plot
%% ==========================
ax1 = nexttile;
hold on;

for k = 1:numFiles

    plot(time,pitch_all(:,k), ...
        'Color',[0.85 0.85 0.85], ...
        'HandleVisibility','off');

    plot(time,roll_all(:,k), ...
        'Color',[0.85 0.85 0.85], ...
        'HandleVisibility','off');

end

plot(time,mean_pitch, ...
    'g', ...
    'LineWidth',2.5, ...
    'DisplayName','Mean Pitch');

plot(time,mean_roll, ...
    'b', ...
    'LineWidth',2.5, ...
    'DisplayName','Mean Roll');

yline(ATTITUDE_LIMIT_DEG, ...
    'r--', ...
    'LineWidth',2, ...
    'DisplayName','+2.25° Requirement');

yline(-ATTITUDE_LIMIT_DEG, ...
    'r--', ...
    'LineWidth',2, ...
    'DisplayName','-2.25° Requirement');

ylabel('Angle (deg)', 'FontSize', AXIS_FONT_SIZE);
set(gca,'FontSize',TICK_FONT_SIZE);
grid on;
ylim([-3 3]);

legend('Location','eastoutside', ...
       'FontSize',LEGEND_FONT_SIZE);

%% ==========================
%% Altitude Plot
%% ==========================
ax2 = nexttile;
hold on;

for k = 1:numFiles

    plot(time,altitude_all_cm(:,k), ...
        'Color',[0.85 0.85 0.85], ...
        'HandleVisibility','off');

end

plot(time,mean_alt_cm, ...
    'b', ...
    'LineWidth',2.5, ...
    'DisplayName','Mean Altitude');

plot(time,target_altitude_cm, ...
    'k--', ...
    'LineWidth',2, ...
    'DisplayName','Target Altitude');

ylabel('Altitude (cm)', 'FontSize', AXIS_FONT_SIZE);
set(gca,'FontSize',TICK_FONT_SIZE);
grid on;

legend('Location','eastoutside', ...
       'FontSize',LEGEND_FONT_SIZE);

%% ==========================
%% Altitude Error Plot
%% ==========================
ax3 = nexttile;
hold on;

for k = 1:numFiles

    err_cm = ...
        (target_altitude - altitude_all(:,k))*100;

    plot(time,err_cm, ...
        'Color',[0.85 0.85 0.85], ...
        'HandleVisibility','off');

end

plot(time,mean_alt_error_cm, ...
    'k', ...
    'LineWidth',2.5, ...
    'DisplayName','Mean Altitude Error');

yline(ALT_ERROR_LIMIT_CM, ...
    'r--', ...
    'LineWidth',2, ...
    'DisplayName','+18 cm Requirement');

yline(-ALT_ERROR_LIMIT_CM, ...
    'r--', ...
    'LineWidth',2, ...
    'DisplayName','-18 cm Requirement');

xlabel('Time (s)', 'FontSize', AXIS_FONT_SIZE);
ylabel('Error (cm)', 'FontSize', AXIS_FONT_SIZE);
set(gca,'FontSize',TICK_FONT_SIZE);

grid on;
ylim([-30 30]);

legend('Location','eastoutside', ...
       'FontSize',LEGEND_FONT_SIZE);

%% ==========================
%% Synchronise X-Axes
%% ==========================
linkaxes([ax1 ax2 ax3],'x');

xlim(ax1,[time(1) time(end)]);
xlim(ax2,[time(1) time(end)]);
xlim(ax3,[time(1) time(end)]);

%% ==========================
%% Overall Figure Title
%% ==========================
sgtitle( ...
    sprintf('Pole-Placement Controller Validation Results', ...
    numFiles), ...
    'FontWeight','bold', ...
    'FontSize',26);