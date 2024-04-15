from gensim import models
model = models.keyedvectors.load_word2vec_format(r'G:\学习\IOT\HAWatcher复现\GoogleNews-vectors-negative300.bin.gz', binary=True)
similarity=model.similarity('woman','man')
print(similarity)
distance = model.distance('woman', 'man')
print(distance)
apple_vector=model.get_vector("apple")
print(apple_vector)
print(model.n_similarity(['i','hate','you'],['happy']))

print(model.n_similarity(['i','love','you'],['happy']))
print(model.similarity('apple','car'))
print(model.similarity('happy','sad'))
print(model.similarity('noodle','death'))