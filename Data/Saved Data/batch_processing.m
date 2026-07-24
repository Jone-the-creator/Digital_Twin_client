%% Load first file as reference time base
numFiles = 1;

data = readtable('practice_result_1.csv');

time_ref = data{:,1};

N = length(time_ref);

yaw_all      = nan(N,numFiles);
pitch_all    = nan(N,numFiles);
roll_all     = nan(N,numFiles);
altitude_all = nan(N,numFiles);

target_altitude = data{:,8};

%% Load and interpolate remaining files
for k = 1:numFiles

    filename = sprintf('practice_result_%d.csv', k);
    data = readtable(filename);

    time = data{:,1};

    yaw      = data{:,2};
    pitch    = data{:,3};
    roll     = data{:,4};
    altitude = data{:,6};

    % Interpolate onto common timeline
    yaw_all(:,k) = interp1(time, yaw, time_ref, ...
        'linear', 'extrap');

    pitch_all(:,k) = interp1(time, pitch, time_ref, ...
        'linear', 'extrap');

    roll_all(:,k) = interp1(time, roll, time_ref, ...
        'linear', 'extrap');

    altitude_all(:,k) = interp1(time, altitude, time_ref, ...
        'linear', 'extrap');
end

time = time_ref;

%% Compute averages
mean_pitch = mean(pitch_all,2);
mean_roll  = mean(roll_all,2);
mean_alt   = mean(altitude_all,2);

mean_alt_error = target_altitude - mean_alt;

%% ==========================
%% Attitude Plot
%% ==========================
figure;
hold on;

% Individual runs (greyed out)
for k = 1:numFiles
    plot(time, pitch_all(:,k), 'Color', [0.8 0.8 0.8], 'HandleVisibility', 'off');
    plot(time, roll_all(:,k),  'Color', [0.8 0.8 0.8], 'HandleVisibility', 'off');
end

% Mean results
plot(time, mean_pitch, 'g', 'LineWidth', 2.5, ...
    'DisplayName', 'Mean Pitch');

plot(time, mean_roll, 'b', 'LineWidth', 2.5, ...
    'DisplayName', 'Mean Roll');

% Requirement bounds ±2 deg
yline( 2, 'r--', 'LineWidth', 2, ...
    'DisplayName', '+2° Requirement');
yline(-2, 'r--', 'LineWidth', 2, ...
    'DisplayName', '-2° Requirement');

xlabel('Time (s)');
ylabel('Angle (deg)');
title('Attitude vs Time (10-run Average)');
legend('Location','best');
grid on;

%% ==========================
%% Altitude Plot
%% ==========================
figure;
hold on;

% Individual altitude runs
for k = 1:numFiles
    plot(time, altitude_all(:,k), ...
        'Color',[0.8 0.8 0.8], 'HandleVisibility', 'off');
end

% Mean altitude
plot(time, mean_alt, 'b', ...
    'LineWidth', 2.5, ...
    'DisplayName', 'Mean Altitude');

% Target altitude
plot(time, target_altitude, ...
    'k--', ...
    'LineWidth', 2, ...
    'DisplayName', 'Target Altitude');

xlabel('Time (s)');
ylabel('Altitude (m)');
title('Altitude vs Time (10-run Average)');
legend('Location','best');
grid on;

%% ==========================
%% Altitude Error Plot
%% ==========================
figure;
hold on;

% Individual errors
for k = 1:numFiles
    err = target_altitude - altitude_all(:,k);
    plot(time, err, 'Color', [0.8 0.8 0.8], 'HandleVisibility', 'off');
end

% Mean error
plot(time, mean_alt_error, 'k', ...
    'LineWidth', 2.5, ...
    'DisplayName', 'Mean Altitude Error');

% Requirement bounds ±0.20 m
yline( 0.20, 'r--', 'LineWidth', 2, ...
    'DisplayName', '+0.20 m Requirement');
yline(-0.20, 'r--', 'LineWidth', 2, ...
    'DisplayName', '-0.20 m Requirement');

xlabel('Time (s)');
ylabel('Altitude Error (m)');
title('Altitude Error vs Time (10-run Average)');
legend('Location','best');
grid on;