clear; clc; close all;

%% ==========================
%% Settings
%% ==========================
numFiles = 10;

%% ==========================
%% Find Shortest Run
%% ==========================
minLength = inf;

for k = 1:numFiles

    filename = sprintf('Validation_Result_%d.csv', k);
    data = readtable(filename);

    minLength = min(minLength, height(data));

end

fprintf('Shortest run length = %d samples\n', minLength);

%% ==========================
%% Preallocate
%% ==========================
pitch_all    = zeros(minLength, numFiles);
roll_all     = zeros(minLength, numFiles);
altitude_all = zeros(minLength, numFiles);

%% ==========================
%% Load Data
%% ==========================
for k = 1:numFiles

    filename = sprintf('Validation_Result_%d.csv', k);
    data = readtable(filename);

    % Trim to shortest run
    pitch_all(:,k)    = data{1:minLength,3};
    roll_all(:,k)     = data{1:minLength,4};
    altitude_all(:,k) = data{1:minLength,6};

    % Use first run as reference
    if k == 1
        time            = data{1:minLength,1};
        target_altitude = data{1:minLength,8};
    end

end

%% ==========================
%% Means
%% ==========================
mean_pitch = mean(pitch_all,2);
mean_roll  = mean(roll_all,2);
mean_alt   = mean(altitude_all,2);

mean_alt_error = target_altitude - mean_alt;

%% ==========================
%% Diagnostics
%% ==========================
fprintf('\n------ Run Limits ------\n');

for k = 1:numFiles

    maxPitch = max(abs(pitch_all(:,k)));
    maxRoll  = max(abs(roll_all(:,k)));

    fprintf('Run %02d | Max Pitch = %.3f deg | Max Roll = %.3f deg\n',...
        k,maxPitch,maxRoll);

end

%% ==========================
%% Attitude Plot
%% ==========================
figure;
hold on;

for k = 1:numFiles

    plot(time,pitch_all(:,k),...
        'Color',[0.8 0.8 0.8],...
        'HandleVisibility','off');

    plot(time,roll_all(:,k),...
        'Color',[0.8 0.8 0.8],...
        'HandleVisibility','off');

end

plot(time,mean_pitch,...
    'g','LineWidth',2.5,...
    'DisplayName','Mean Pitch');

plot(time,mean_roll,...
    'b','LineWidth',2.5,...
    'DisplayName','Mean Roll');

yline(2,...
    'r--','LineWidth',2,...
    'DisplayName','+2° Requirement');

yline(-2,...
    'r--','LineWidth',2,...
    'DisplayName','-2° Requirement');

xlabel('Time (s)');
ylabel('Angle (deg)');

title(sprintf('Attitude vs Time (%d-Run Average)',numFiles), ...
    'Jonah Habel - Test Flight I - 22.07.2026');

legend('Location','best');
grid on;
ylim([-3 3]);

%% ==========================
%% Altitude Plot
%% ==========================
figure;
hold on;

for k = 1:numFiles

    plot(time,altitude_all(:,k),...
        'Color',[0.8 0.8 0.8],...
        'HandleVisibility','off');

end

plot(time,mean_alt,...
    'b','LineWidth',2.5,...
    'DisplayName','Mean Altitude');

plot(time,target_altitude,...
    'k--','LineWidth',2,...
    'DisplayName','Target Altitude');

xlabel('Time (s)');
ylabel('Altitude (m)');

title(sprintf('Altitude vs Time (%d-Run Average)',numFiles), ...
    'Jonah Habel - Test Flight I - 22.07.2026');

legend('Location','best');
grid on;

%% ==========================
%% Altitude Error Plot
%% ==========================
figure;
hold on;

for k = 1:numFiles

    err = target_altitude - altitude_all(:,k);

    plot(time,err,...
        'Color',[0.8 0.8 0.8],...
        'HandleVisibility','off');

end

plot(time,mean_alt_error,...
    'k','LineWidth',2.5,...
    'DisplayName','Mean Altitude Error');

yline(0.25,...
    'r--','LineWidth',2,...
    'DisplayName','+0.25 m Requirement');

yline(-0.25,...
    'r--','LineWidth',2,...
    'DisplayName','-0.25 m Requirement');

xlabel('Time (s)');
ylabel('Altitude Error (m)');

title(sprintf('Altitude Error vs Time (%d-Run Average)',numFiles), ...
    'Jonah Habel - Test Flight I - 22.07.2026');

legend('Location','best');
grid on;
ylim([-0.5 0.5]);