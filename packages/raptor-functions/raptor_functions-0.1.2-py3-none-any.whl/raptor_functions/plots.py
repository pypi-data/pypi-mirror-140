



def plot_sensor_signals(df, sensors_signals_col, target_col_name):
        
    facetgrid = sns.FacetGrid(df, hue=target_col_name, height=5,aspect=3)
    facetgrid.map(sns.distplot, sensors_signals_col, hist=False).add_legend()


def signals_plot_by_target(df, target_col_name, labels):
    fig, axes = plt.subplots(nrows=24,ncols=2, figsize=(20,36))
    df[df[target_col_name]==labels[0]].iloc[:, 1:25].plot(ax=axes[:,0], subplots=True, sharex=True, figsize=(10,25))

    df[df[target_col_name]==labels[1]].iloc[:, 1:25].plot(ax=axes[:,1], subplots=True, sharex=True, figsize=(10,25));

    # plt.legend()

    axes[0][0].set_title(labels[0])
    axes[0][1].set_title(labels[1])

    plt.show();




def plot_by_exp_stage():
    fig, axes = plt.subplots(nrows=24,ncols=5, figsize=(20,36))
    df[df['exp_stage']=='baseline'].iloc[:, 1:25].plot(ax=axes[:,0], subplots=True, sharex=True, figsize=(10,25))

    df[df['exp_stage']=='absorb'].iloc[:, 1:25].plot(ax=axes[:,1], subplots=True, sharex=True, figsize=(10,25));
    df[df['exp_stage']=='pause'].iloc[:, 1:25].plot(ax=axes[:,2], subplots=True, sharex=True, figsize=(10,25));
    df[df['exp_stage']=='desorb'].iloc[:, 1:25].plot(ax=axes[:,3], subplots=True, sharex=True, figsize=(10,25));
    df[df['exp_stage']=='flush'].iloc[:, 1:25].plot(ax=axes[:,4], subplots=True, sharex=True, figsize=(10,25));

    # plt.legend()

    axes[0][0].set_title('baseline')
    axes[0][1].set_title('absorb')
    axes[0][2].set_title('pause')
    axes[0][3].set_title('desorb')
    axes[0][4].set_title('flush')





def plot_new_sample(model, x_train, x):
    fig, ax = plt.subplots()
    x = x.reshape(1,-1)
    ax.scatter(x_train[:,0], x_train[:,1], c=l)
    ax.scatter(x[:,0], x[:,1])
# 
def sensor_channel_response_bar(df,date_time,x_columns):
  df = df[x_columns]
  x = df.columns.tolist()
  # 
  fig = plt.figure()
  plt.title(str(date_time))
  for i in range(len(df)):
    y = df.iloc[i].values.tolist()
    plt.bar(x, y)
    plt.show()
    plt.ylim([0,500])
    plt.ylabel('mV')
    fig = plt.gcf()
    fig.autofmt_xdate()
    sleep(0.05)
    clear_output(wait=True)

def sensor_channel_response_line(df,date_time,x_columns):
  df = df[x_columns]
  x = df.columns.tolist()
  y = df.values.tolist()
  # 
  fig = plt.figure()
  plt.title(str(date_time))
  plt.plot(y)
  plt.ylim([0,500])
  plt.ylabel('mV')
  fig = plt.gcf()
  fig.autofmt_xdate()
  plt.legend(x)
  plt.show()




def plot_voc_signal_sensors(control, covid):

    fig, axes = plt.subplots(nrows=24,ncols=1, figsize=(25,42))

    control.iloc[:, 3:27].plot(subplots=True, sharex=True, figsize=(10,25), color='b', label='Control', legend=False, ax=axes);
    covid.iloc[:, 3:27].plot(subplots=True, sharex=True, figsize=(10,25), color='r', label='Covid', legend=False, ax=axes);
    axes[0].set_title('VOC Signature After Normalisation', fontsize=20);
    fig.text(0.5, 0.11, 'Time Steps', ha='center', fontsize=16);
    fig.text(0.1, 0.5, 'Magnitude of Voltage Signals', va='center', rotation='vertical', fontsize=16);
    plt.legend({'Control','Covid'}, fontsize=16);
    fig.savefig('new_data.jpeg');


def plot_voc_sensor(covid, control):

    fig, ax = plt.subplots(figsize=(14, 6), dpi=80)
    ax.plot(covid['sensor_1'], label='Covid', color='blue', animated = True, linewidth=1)
    ax.plot(control['sensor_1'], label='Control', color='red', animated = True, linewidth=1)


def plot_sensor_mean(df, cols):
    ax = df[cols].mean().plot(kind='bar', figsize=(10,6), title="Features Standard Deviation", label='covid')
    df[cols].mean().plot(kind='bar', figsize=(10,6), title="Features Standard Deviation", ax=ax, color='red', alpha=0.3, label='control');
    plt.legend();