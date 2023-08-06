import os, tempfile, subprocess
import pandas as pd


def irt_ensemble(data):

    inFile = tempfile.NamedTemporaryFile(delete=False)
    outFile = tempfile.NamedTemporaryFile(delete=False)
    try:
        data.to_csv(inFile, index=False)
        subprocess.call (["/usr/bin/Rscript", "--vanilla", "qc/script.r", inFile.name, outFile.name])

        if outFile:
            try:
                out = pd.read_csv(outFile)
            except:
                out = None
        else:
            out = None

    finally:
        inFile.close()
        outFile.close()
        os.unlink(inFile.name)
        os.unlink(outFile.name)

    return out


if __name__ == '__main__':
    import numpy as np
    data = np.random.randn(100, 2)
    df = pd.DataFrame(data, columns=['x', 'y'])

    out = irt_ensemble(df)
    print(out)
