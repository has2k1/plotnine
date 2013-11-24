from ggplot import *



df = pd.DataFrame({
    "x": range(100),
    "y": np.random.choice([-1, 1], 100)
})

df.y = df.y.cumsum()

p = ggplot(aes(x='x', y='y'), data=df)
print p + geom_step()
plt.show(True)

