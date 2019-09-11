library(ggplot2)

df = data.frame(
				x = c('A','B','B','C','C','D','D','D','D'),
				y= c(0, 100,100, 100, 150, 0, 100, 100, 150))
g = ggplot(df)
g = g + geom_violin(aes(x,y))
ggsave(plot=g, filename='test.png')
