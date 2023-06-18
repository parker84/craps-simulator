import streamlit as st
import altair as alt
import pandas as pd
from millify import millify
from craps_simulator import CrapsSimulator
from tqdm import tqdm
import os
import coloredlogs, logging
logger = logging.getLogger(__name__)
coloredlogs.install(level=os.getenv('LOG_LEVEL', 'INFO'))

# --------------setup
st.set_page_config(
    page_title='Craps Simulator', 
    page_icon='🎲', 
    initial_sidebar_state="auto", 
    menu_items=None,
    layout='wide'
)
st.title("Craps Simulator 🎲")
st.markdown('**Purpose**: The purpose of this app is to enable craps gamblers to understand the probabilities of different outcomes based on their betting strategy.')

# st.markdown('### Place Your Bets')
col1, col2 = st.columns(2)

with col1:
    bet_type = st.selectbox(
        'Bet Type 🎲', 
        [
            'Pass Line Bet',
            'Don\'t Pass Bet'
        ], index=0,
        help='To learn more about craps strategy / bets see here: https://www.mypokercoaching.com/craps-strategy/'
    )
with col2:
    bet_amount = st.number_input(
        'Bet Amount 🎰',
        min_value=1,
        max_value=1000000,
        value=50,
        help='The amount of money you are betting on every roll.'
    )

# st.markdown('### Set Your Strategy')

col1, col2 = st.columns(2)

with col1:
    stop_loss = st.number_input(
        'Stop Loss 🔻',
        min_value=-1000000,
        max_value=0,
        value=-1000,
        help='The amount of money you are willing to lose before you stop playing.'
    )

with col2:
    stop_win = st.number_input(
        'Stop Win 💰',
        min_value=0,
        max_value=1000000,
        value=500,
        help='The amount of money, at which if you win this amount, you\'ll stop playing.'
    )

with st.expander('Advanced Settings ⚙️', expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        max_rolls_per_game = st.number_input(
            "Max Number of Rolls Per Game 🎲",
            min_value=1,
            max_value=10000,
            value=100,
            help='The maximum number of rolls you\'ll play before stopping.'
        )
    with col2:
        games_to_sim = st.number_input(
            "Number of Games to Simulate 🤖",
            min_value=1,
            max_value=1000000,
            value=100000,
            help='The number of games we\'ll simulate to estimate probabilities.'
        )

# --------------simulation
st.markdown('### Simulation Results 📊')

simulator = CrapsSimulator(
    bet_type=bet_type,
    bet_amount=bet_amount,
    stop_loss=stop_loss,
    stop_win=stop_win,
    max_rolls_per_game=max_rolls_per_game,
    games_to_sim=games_to_sim
)

results = []
logger.info(f'Running {games_to_sim} Game Simulations')
progress_text = f"Simulating `{millify(games_to_sim)}` Craps 🎲 Games..."
my_bar = st.progress(0, text=progress_text)

# for game in tqdm(range(games_to_sim)):
for game in range(games_to_sim):
    if game % 1000 == 0:
        percent_complete = int(((game) / games_to_sim) * 100)
        my_bar.progress(percent_complete, text=progress_text)
    game_result = simulator.play_game()
    results.append(game_result)
my_bar.empty()

simulation_results_df = pd.DataFrame(results)
simulation_results_df['win'] = simulation_results_df['result'] == stop_win
simulation_results_df['loss'] = simulation_results_df['result'] == stop_loss
simulation_results_df['incomplete'] = (simulation_results_df['result'] != stop_win) * (simulation_results_df['result'] != stop_loss)
simulation_results_df['positive'] = simulation_results_df['result'] > 0 
simulation_results_df['negative'] = simulation_results_df['result'] < 0
simulation_results_df['zero'] = simulation_results_df['result'] == 0

viz_df = pd.DataFrame([])
viz_df['Result'] = [
    f"1) 💰 Won ${millify(stop_win)}",
    f"2) ❌ Lost ${millify(-stop_loss)}",
    f"3) 🤷‍♀️ No Limit Hit",
]
viz_df['Probability'] = [
    simulation_results_df['win'].mean(),
    simulation_results_df['loss'].mean(),
    simulation_results_df['incomplete'].mean()
]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label=f"💰 % of Games Won `${millify(stop_win)}`",
        value=f"{round(simulation_results_df['win'].mean() * 100, 1)}%",
    )
with col2:
    st.metric(
        label=f"❌ % of Games Lost `${millify(-stop_loss)}`",
        value=f"{round(simulation_results_df['loss'].mean() * 100, 1)}%",
    )
with col3:
    st.metric(
        label=f"🤷‍♀️ % of Games Stopped at `{max_rolls_per_game}` Rolls",
        value=f"{round(simulation_results_df['incomplete'].mean() * 100, 1)}%",
    )

bars = alt.Chart(viz_df).mark_bar().encode(
    y='Result',
    x = alt.Y("Probability", axis=alt.Axis(format='%'))
)
plot = (bars).properties(
    title="Probability of Hitting Stop Win / Loss Limits"
).interactive()
st.altair_chart(plot, use_container_width=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Average Amount at End of Game 🤑",
        value=f"${round(simulation_results_df['result'].mean(), 1)}",
    )
with col2:
    st.metric(
        label=f"% of Games Ending Positive 🟢",
        value=f"{round(simulation_results_df['positive'].mean() * 100, 1)}%",
    )
with col3:
    st.metric(
        label=f" % of Games Ending Negative 🔴",
        value=f"{round(simulation_results_df['negative'].mean() * 100, 1)}%",
    )
with col4:
    st.metric(
        label=f"% of Games Ending at `$0` 🟡",
        value=f"{round(simulation_results_df['zero'].mean() * 100, 1)}%",
    )

viz_df = pd.DataFrame([])
viz_df['Result'] = [
    "1) Positive 🟢",
    "2) Negative 🔴",
    "3) Zero 🟡",
]
viz_df['Probability'] = [
    simulation_results_df['positive'].mean(),
    simulation_results_df['negative'].mean(),
    simulation_results_df['zero'].mean()
]

bars = alt.Chart(viz_df).mark_bar().encode(
    y='Result',
    x = alt.Y("Probability", axis=alt.Axis(format='%'))
)
plot = (bars).properties(
    title="Probability of Ending Positive / Negative / Zero"
).interactive()
st.altair_chart(plot, use_container_width=True)

# --------------runs over time
with st.expander('Simulation Results Per Roll 📉'):
    results_df = pd.DataFrame([
        row for row in simulation_results_df['results']
    ])
    metrics_of_cumulative_results = results_df.aggregate(['mean', 'median', 'min', 'max', 'std']).T
    metrics_of_cumulative_results['Roll'] = metrics_of_cumulative_results.index + 1
    metrics_of_cumulative_results['Average Win / Loss'] = metrics_of_cumulative_results['mean']
    metrics_of_cumulative_results['upper'] = metrics_of_cumulative_results['mean'] + metrics_of_cumulative_results['std']
    metrics_of_cumulative_results['lower'] = metrics_of_cumulative_results['mean'] - metrics_of_cumulative_results['std']

    line = alt.Chart(metrics_of_cumulative_results).mark_line().encode(
        x='Roll',
        y=alt.Y("Average Win / Loss", axis=alt.Axis(format='$s'))
    )
    error_band = alt.Chart(metrics_of_cumulative_results).mark_errorband().encode(
        x='Roll',
        y="Average Win / Loss",
        yError='upper',
        yError2='lower',
    )
    plot = (line + error_band).properties(
        title="Average Win / Loss Per Roll"
    ).interactive()
    st.altair_chart(plot, use_container_width=True)
    


st.markdown('---')
st.markdown(f'`{millify(games_to_sim)}` games simulated, [see github here](https://github.com/parker84/craps-simulator)')