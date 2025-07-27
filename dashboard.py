import pandas as pd
import plotly.express as px
import streamlit as st

# LOAD DATA
df = pd.read_csv('imdb top 1000/imdb_clean.csv')

# DASHBOARD TITLE
st.title("🎬 IMDb Top 1000 Movies Dashboard")

# CLEAN COLUMN NAMES FOR INTERNAL USE: lowercase and replace spaces with underscores
df.columns = [col.strip().replace(' ', '_').lower() for col in df.columns]
# -> Rename for ease of use
df.rename(columns={'series_title': 'title', 'released_year': 'release_year'}, inplace=True)
# -> Drop rows with missing essential data
df.dropna(subset=['release_year', 'rating', 'genre'], inplace=True)


#ENSURE CORRECT DATAYPE
# -> Ensure release_year is an integer
# -> For sliders and histograms, we need release_year to be numeric not string
df['release_year'] = df['release_year'].astype(int)
# -> Ensure runtime is numeric (handle cases like '148 min' strings)
df['runtime'] = df['runtime'].astype(str).str.extract('(\d+)')  # Extract numeric part ('148')
df['runtime'] = pd.to_numeric(df['runtime'], errors='coerce')   # Convert to numeric (148)

# SIDEBAR FILTERS
# -> Sidebar Heading
st.sidebar.header("🔍 Customize Your Movie Search")
# -> Choose Genres
selected_genre = st.sidebar.multiselect("🎬 Choose Genres", options=sorted(df['genre'].dropna().unique()), help="Choose your preferred genres to include it in results")
# -> Minimum IMDb Rating
min_rating = st.sidebar.slider("⭐ Minimum IMDb Rating", 5.0, 10.0, 7.0, step=0.1, help="Choose your preferred rating")
# -> Released After Year
selected_year = st.sidebar.slider("📅 Released After Year", 1950, 2022, 2000, help="Choose your preferred year of release")
# -> Filter dataset
filtered_df = df[
    # -> Ensures genre selected should be equal to what the user selected
    (df['genre'].isin(selected_genre)) &
    # -> Ensures rating should be equal to or more than what user selected
    (df['rating'] >= min_rating) &
    # -> Ensures release year should be equal to or more than what user selected
    (df['release_year'] >= selected_year)
]

# USER-FRIENDLY TABLE
# -> Display version with clean headers
display_df = filtered_df.copy()
display_df.rename(columns={
    'title': 'Title',
    'director': 'Director',
    'release_year': 'Release Year',
    'runtime': 'Runtime',
    'genre': 'Genre',
    'rating': 'IMDb Rating',
    'metascore': 'Metascore',
    'gross(m)': 'Gross (M)'
}, inplace=True)
# -> To display Runtime in the format of X hrs Y min instead of just mins
display_df['Runtime'] = display_df['Runtime'].apply(
    lambda x: f"{int(x)//60} hr {int(x)%60} min" if pd.notna(x) else "N/A"
)
# -> Displays the top 20 movies in the table according to the preferences of the user
st.dataframe(display_df.head(20))

# QUICK STATS SECTION
# -> Gives the heading "Quick Stats"
st.markdown("## 🔍 Quick Stats")
# -> Creates 3 columns side by side for visual balance 
col1, col2, col3 = st.columns(3)
# -> Shows Total Movies(col1)
col1.metric("Total Movies", filtered_df.shape[0])
# -> Calculates & shows Avg Ratings rounded to 2 decimals(col2)
col2.metric("Avg Rating", round(filtered_df['rating'].mean(), 2))
# -> Calculate mean runtime from filtered movies(col3)
avg_runtime = filtered_df['runtime'].mean()
# Converts avg runtime from mins to hrs and mins
if pd.notna(avg_runtime):
    hours = int(avg_runtime) // 60
    minutes = int(avg_runtime) % 60
    col3.metric("Avg Runtime", f"{hours} hr {minutes} min")
else:
    # -> Handle cases where runtime is NaN to avoid crash
    col3.metric("Avg Runtime", "N/A")

# TOP 10 RATED MOVIES BAR CHART
# -> Adds a bold title on the dashboard 
#st.markdown("## 🏆 Highest Rated Films")
# -> Sort movies by imdb ratings in descending order 
top_movies = filtered_df.sort_values(by='rating', ascending=False).head(20)
# ->  Creates a colorful bar chart with x_axis = title, y_axis = rating, color given based on the genres
fig1 = px.bar(top_movies, x='title', y='rating', color='genre', text='rating', hover_data=['release_year'])
# -> Displays the bar chart across the full Streamlit container width.
#st.plotly_chart(fig1, use_container_width=True)

# MOVIE RELEASE TREND HISTOGRAM
# -> Adds a bold title on the dashboard
#st.markdown("## 📊 Movie Release Trend")(Not used because of chart selector)
# -> Creates a histogram that shows how many movies came out in each year
fig2 = px.histogram(filtered_df, x='release_year', nbins=15, title="Movies per Year")
# -> Displays the histogram across the full Streamlit container width.
#st.plotly_chart(fig2, use_container_width=True)(Not used because of chart selector)

# GENRE DISTRIBUTION PIE CHART
# -> Adds a bold title on the dashboard
#st.markdown("## 🍿 Genre Distribution")(Not used because of chart selector)
# -> Makes a circular pie chart as hole=0, as hole increases it creates a hole in the chart
fig3 = px.pie(filtered_df, names='genre', title="Genre Breakdown", hole=0)
# -> Displays the pie chart across the full Streamlit container width.
#st.plotly_chart(fig3, use_container_width=True)(Not used because of chart selector)

# CHART SELECTOR
st.markdown("## 📈 Visual Insights")
chart_type = st.selectbox("Choose Chart", ["Bar Chart", "Pie Chart"])

if chart_type == "Bar Chart":
    st.plotly_chart(fig1, use_container_width=True)
elif chart_type == "Pie Chart":
    st.plotly_chart(fig3, use_container_width=True)

# MOVIE RELEASE TREND ALWAYS SHOWN
st.markdown("## 📊 Movie Release Trend")
st.plotly_chart(fig2, use_container_width=True)
