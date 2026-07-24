% Load CSV file
filename = 'Validation_result_1.csv';
data = readtable(filename);

% Extract columns
time = data{:,1};
yaw = data{:,2};
pitch = data{:,3};
roll = data{:,4};
battery = data{:,5};
altitude = data{:,6};
loop_rate = data{:,7};
target_altitude = data{:,8};

% Display basic info
fprintf('Loaded %d samples\n', length(time));

%% Attitude Plot
figure;

hold on;
plot(time, pitch, 'g', 'DisplayName', 'Pitch');
plot(time, roll, 'b', 'DisplayName', 'Roll');
% plot(time, yaw, 'r', 'DisplayName', 'Yaw');

xlabel('Time (s)');
ylabel('Angle (deg)');
title('Attitude vs Time');
legend;
grid on;

%% Altitude Plot
figure;

plot(time, altitude, 'b', ...
    'LineWidth', 1.5, ...
    'DisplayName', 'Measured Altitude');

hold on;

plot(time, target_altitude, 'r--', ...
    'LineWidth', 2, ...
    'DisplayName', 'Target Altitude');

error = target_altitude - altitude;

plot(time, error, 'k', 'LineWidth', 1.5, 'DisplayName', 'Altitude Error');

xlabel('Time (s)');
ylabel('Altitude (m)');
title('Altitude vs Time');
legend('Location', 'best');
grid on;

%% Battery Level Plot
% figure;
% plot(time, battery, 'k');
% xlabel('Time (s)');
% ylabel('Battery (%)');
% title('Battery Level');
% grid on;

%% Loop Rate Plot
% figure;
% plot(time, loop_rate, 'k');
% xlabel('Time (s)');
% ylabel('Rate (Hz)');
% title('Control Loop Rate');
% grid on;

%% Statistics
fprintf('Yaw mean: %.2f deg\n', mean(yaw));
fprintf('Pitch mean: %.2f deg\n', mean(pitch));
fprintf('Roll mean: %.2f deg\n', mean(roll));
fprintf('Altitude mean: %.3f m\n', mean(altitude));
fprintf('Altitude min: %.3f m\n', min(altitude));
fprintf('Altitude max: %.3f m\n', max(altitude));
fprintf('Battery min: %.2f %%\n', min(battery));