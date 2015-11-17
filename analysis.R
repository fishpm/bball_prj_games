rm(list=ls())

library(randomForest)
library(e1071)
library(beeswarm)

####
## FUNCTIONS START
####

## Performance metrics for logistic model
perf <- function(model,df){
  
  # Performance table.
  pred <- as.numeric(predict(model, df[cv,], type='response') > 0.5)
  actual <- df[cv,'win.numeric']
  perf_table <- table(pred,actual)
  
  # Precision, recall, F1 and accuracy scores.
  precision <- perf_table['1','1']/(perf_table['1','1'] + perf_table['1','0'])
  recall <- perf_table['1','1']/(perf_table['1','1'] + perf_table['0','1'])
  f1 <- 2*((precision*recall)/(precision+recall))
  acc <- (sum(diag(perf_table))/sum(perf_table))*100
  
  perf_out <- list('acc' = acc, 'f1' = f1, 'perf' = perf_table)
  return(perf_out)
}

# Permute assignment to train/cv/test sets and compute logistic model
part_fit <- function(df){
  
  # Partition data.
  train <- sample(n, round(n*0.8))
  cv <- sample(seq(n)[-train],round(n*0.2))
  test <- seq(n)[-c(train,cv)]
  
  ## Logisitic regression model
  f <- paste('win.numeric ~ ', paste(c(hnames, anames), collapse = ' + '), sep = '')
  l <- glm(f, family = binomial(logit), data = dd[train,])
  
  #Compute performance metrics with perf function.
  perf(l,dd)
}

## Learning curves.
lc <- function(i){
  
  # Logistic model
  l <- glm(f,family=binomial(logit), data = dd[train[1:i],])
  
  # Training error.
  train_err <- -mean(dd[train[1:i], 'win.numeric']*log(predict(l, dd[train[1:i], ], type='response')) + (1 - dd[train[1:i],'win.numeric'])*log(1-predict(l, dd[train[1:i],], type='response')))
  
  # Test/CV error.
  cv_err <- -mean(dd[cv,'win.numeric']*log(predict(l, dd[cv,], type='response')) + (1-dd[cv,'win.numeric'])*log(1-predict(l, dd[cv,], type='response')))
  c(train_err,cv_err)
}

####
## FUNCTIONS END
####

# Up to date stats for each starter for each team for each game.
data <- read.csv('~/Documents/projects/bball_prj_games/UTD_2014.csv')
# Winners
outcome <- read.csv('~/Documents/projects/bball_prj_games/GL2014.csv')

# Statistics to be pulled from UTD .csv
# obp = on-base percentage, slg = slugging
hnames <- c(paste('h', seq(9), '_obp', sep=''), paste('h', seq(9), '_slg', sep=''))
anames <- c(paste('a', seq(9), '_obp', sep=''), paste('a', seq(9), '_slg', sep=''))

# Merge player statistics and game outcome information into single df.
dd0 <- data[,c('game', hnames, anames)]
dd <- merge(dd0, outcome, by.x = 'game', by.y = 'game_id')

# n games
n <- dim(dd)[1]

# Partition train/cv/test samples
train <- sample(n, round(n*0.8))
cv <- sample(seq(n)[-train],round(n*0.2))
test <- seq(n)[-c(train,cv)]

# home team win == 1
dd$win.numeric <- as.numeric(dd[,'winner'])-1

# Logistic model.
f <- as.formula(paste('win.numeric ~ ', paste(c(hnames, anames), collapse = ' + '), sep = ''))
l <- glm(f, family = binomial(logit), data = dd[train,])
summary(l)

# Performance table.
pred <- as.numeric(predict(l, dd[cv,], type='response') > 0.5)
actual <- dd[cv,'win.numeric']
perf_table <- table(pred,actual)

# Precision, recall, F1 and accuracy scores.
precision <- perf_table['1','1']/(perf_table['1','1'] + perf_table['1','0'])
recall <- perf_table['1','1']/(perf_table['1','1'] + perf_table['0','1'])
f1 <- 2*((precision*recall)/(precision+recall))
acc <- (sum(diag(perf_table))/sum(perf_table))*100

print('*** LOGISTIC MODEL PERFORMANCE METRICS ***')
print('*** Prediction table ***')
print(perf_table)
print(paste('F1: ', signif(f1,3), '; Precision: ', signif(precision,3), '; Recall: ', signif(recall,3), sep = ''))
print(paste('Accuracy: ', signif(acc), '%', sep = ''))

######
## randomForest model START
######

# Model
f <- as.formula(paste('winner ~ ', paste(c(hnames, anames), collapse = ' + '), sep = ''))
rF <- randomForest(f, data = dd[train,])

# Performance table.
pred <- predict(rF, dd[cv,], type='response')
actual <- dd[cv,'winner']
perf_table <- table(pred,actual)

# Precision, recall, F1 and accuracy scores.
precision <- perf_table['home','home']/(perf_table['home','home'] + perf_table['home','away'])
recall <- perf_table['home','home']/(perf_table['home','home'] + perf_table['away','home'])
f1 <- 2*((precision*recall)/(precision+recall))
acc <- (sum(diag(perf_table))/sum(perf_table))*100

print('*** RANDOM FOREST PERFORMANCE METRICS ***')
print('*** Prediction table ***')
print(perf_table)
print(paste('F1: ', signif(f1,3), '; Precision: ', signif(precision,3), '; Recall: ', signif(recall,3), sep = ''))
print(paste('Accuracy: ', signif(acc), '%', sep = ''))

######
## randomForest model END
######

######
## SVM START
######

# Model
f <- as.formula(paste('winner ~ ', paste(c(hnames, anames), collapse = ' + '), sep = ''))
svm <- svm(f, data = dd[train,])

# Performance table.
pred <- predict(svm, dd[cv,], type='response')
actual <- dd[cv,'winner']
perf_table <- table(pred,actual)

# Precision, recall, F1 and accuracy scores.
precision <- perf_table['home','home']/(perf_table['home','home'] + perf_table['home','away'])
recall <- perf_table['home','home']/(perf_table['home','home'] + perf_table['away','home'])
f1 <- 2*((precision*recall)/(precision+recall))
acc <- (sum(diag(perf_table))/sum(perf_table))*100

print('*** SVM PERFORMANCE METRICS ***')
print('*** Prediction table ***')
print(perf_table)
print(paste('F1: ', signif(f1,3), '; Precision: ', signif(precision,3), '; Recall: ', signif(recall,3), sep = ''))
print(paste('Accuracy: ', signif(acc), '%', sep = ''))

######
## SVM END
######

####
## PERMUTATION TESTS START
####

# N permutations
n_perm <- 100

# Partition data into train/test sets, fit logistic model and compute performance metrics.
performance <- lapply(seq(n_perm), function(i) part_fit(dd))
acc_all <- sapply(performance, with, acc)
f1_all <- sapply(performance, with, f1)

# Plot summary outputs.
pdf('~/Documents/projects/bball_prj_games/perm_acc.pdf')

# Naive accuracy (i.e., home-team win pct)
hwin <- mean(dd$win.numeric)*100

# Plot observed accuracy for n_perm permutations.
beeswarm(acc_all, pch = 19, las = 1, bty = 'l', ylab = 'Accuracy')
title(main = 'Model performance: permutation results')
legend('topleft', lty = c(2,1), col = c('gray','black'), legend = c('Home WP'  ,'Mean Acc'), bty = 'n')
lines(c(0.8,1.2), rep(hwin,2), lwd = 3, lty = 2, col = 'gray')
lines(c(0.8,1.2), rep(mean(acc_all),2), lwd = 3, col = 'black')
mtext(paste('Mean Acc: ', signif(mean(acc_all),4), '%; Home WP: ', signif(hwin,4), '%', sep = ''))

dev.off()

####
## PERMUTATION TESTS END
####

#######
### LEARNING CURVES
#######

# Choose min sample size based on # of predictors.
min_n <- ceiling(dim(dd)[2]/10)*10+50
n10 <- seq(min_n, length(train) ,10)

# Compute training and cross-validation errors.
out <- lapply(n10, function(i) lc(i))
err <- cbind(unlist(data.frame(out)[1,]), unlist(data.frame(out)[2,]))
rownames(err) <- paste('N',n10,sep='')
colnames(err) <- c('train','cv')

# Plot training and cv errors.
pdf('~/Documents/projects/bball_prj_games/learning_curve.pdf')

# Training error.
plot(err[,'train'] ~ n10, pch=19, bty = 'l', las = 1, xlab = 'Sample size', ylab = 'Error', ylim = range(err), xlim = c(1000,2000))
# Testing error.
points(err[,'cv'] ~ n10, pch=19, bty = 'l', las = 1, xlab = 'Sample size', ylab = 'Error',col = 'blue')
title(main = "Learning curve: Up-to-date game information predicting game outcomes.")

plot(err[,'train'] ~ n10, pch=19, bty = 'l', las = 1, xlab = 'Sample size', ylab = 'Error', ylim = range(err))
points(err[,'cv'] ~ n10, pch=19, bty = 'l', las = 1, xlab = 'Sample size', ylab = 'Error',col = 'blue')
lines(n10, err[,'train'])
lines(n10, err[,'cv'], col = 'blue')
title(main = "Learning curve: Up-to-date game information predicting game outcomes.", sub = 'Sample size: 1000-2000')

dev.off()