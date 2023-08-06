# Datomizer pip package
## Welcome to Datomize python client
[Datomizer Docs](https://datomize.github.io/datomizeSDK) <br />
###Usage Example:

    from datomizer import Datomizer, DatoMapper, DatoTrainer, DatoGenerator
    
    datomizer = Datomizer(username=username, password=password)
    
    mapper = DatoMapper(datomizer)
    mapper.discover(df=df, title="Some Title")
    
    trainer = DatoTrainer(mapper)
    trainer.train()

    generator = DatoGenerator(trainer)
    generator.generate()
    dato_df = pd.read_csv(generator.get_generated_data_csv())

###Async Usage Example

    from datomizer import Datomizer, DatoMapper, DatoTrainer, DatoGenerator
    
    datomizer = Datomizer(username=username, password=password)
    
    mapper = DatoMapper(datomizer)
    mapper.discover(df=df, title="Some Title", wait=False)
    ...do something...
    mapper.wait()
    
    trainer = DatoTrainer(mapper)
    trainer.train(wait=False)
    ...do something...
    trainer.wait()
    

    generator = DatoGenerator(trainer)
    generator.generate(wait=False)
    ...do something...
    generator.wait()
    dato_df = pd.read_csv(generator.get_generated_data_csv())