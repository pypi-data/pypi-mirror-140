def load_cfg():
    from hydra import initialize_config_dir, compose
    from dotenv import load_dotenv

    load_dotenv()
    import os

    cur_dir = os.path.abspath(os.path.join(__file__, "../../"))
    conf_dir = f"{cur_dir}/conf"

    with initialize_config_dir(config_dir=conf_dir):
        cfg = compose("config")

    return cfg
