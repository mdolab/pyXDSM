def chunk_label(label, n_chunks):
    for i in range(0, len(label), n_chunks):
        yield label[i : i + n_chunks]