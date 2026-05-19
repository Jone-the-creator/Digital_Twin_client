% Load CSV file
filename = 'recording_2026-05-19_10-17-16.csv';  % change to your file name
data = readtable(filename);

% Extract columns (adjust names if MATLAB modifies them)
time = data{:,1};       % time (s)
yaw = data{:,2};
pitch = data{:,3};
roll = data{:,4};
battery = data{:,5};

% Display basic info
fprintf('Loaded %d samples\n', length(time));

% Plot orientation over time
figure;
% plot(time, yaw, 'r', 'DisplayName','Yaw'); 
hold on;
plot(time, pitch, 'g', 'DisplayName','Pitch');
plot(time, roll, 'b', 'DisplayName','Roll');
xlabel('Time (s)');
ylabel('Angle (deg)');
title('Attitude vs Time');
legend;
grid on;

% Plot battery level
% figure;
% plot(time, battery, 'k');
% xlabel('Time (s)');
% ylabel('Battery (%)');
% title('Battery Level');
% grid on;

% Example: compute statistics
fprintf('Yaw mean: %.2f deg\n', mean(yaw));
fprintf('Pitch mean: %.2f deg\n', mean(pitch));
fprintf('Roll mean: %.2f deg\n', mean(roll));
fprintf('Battery min: %.2f %%\n', min(battery));