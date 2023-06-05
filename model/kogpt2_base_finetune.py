import argparse

from kogpt2_finetune import train

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # data_arg
    parser.add_argument("--output_dir", type=str, default="./output/kogpt2")
    parser.add_argument(
        "--data_dir", type=str, default="./data/poem_data/"
    )
    parser.add_argument("--model_name_or_path", type=str, default="skt/kogpt2-base-v2")
    parser.add_argument("--train_filename", type=str, default="poem_preprocess_data.xlsx")
    parser.add_argument("--data_split_ratio", type=float, default=0.9, help="train data ratio")

    # train_arg
    parser.add_argument("--num_train_epochs", type=int, default=10)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--seq_len", type=int, default=256)

    # huggingface_arg
    parser.add_argument("--repo_name", type=str, help='huggingface repository name')
    parser.add_argument("--auth_token", type=str, help='huggingface auth token')

    args = parser.parse_args()
    train(args)
