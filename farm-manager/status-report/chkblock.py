#!/usr/bin/env python2


def chkblock(data, data0):
    luckyID = []
    i = 0
    for mminer in data:
        j = 0
        try:
            mminer0 = data0[i]
        except:
            pass
        for miner in mminer[1:]:
            try:
                miner0 = mminer0[j + 1]
            except:
                pass
            try:
                block0 = int(miner0[7])
            except:
                block0 = 0
            try:
                block_archive0 = int(miner0[8])
            except:
                block_archive0 = 0

            block = int(miner[7])
            if block < block0:
                miner.append(str(block_archive0 + block0))
                if block > 0:
                    luckyID.append({'id': mminer[0] + ':' + miner[0],
                                    'num': str(block)})
            elif block == block0:
                miner.append(str(block_archive0))
            else:
                miner.append(str(block_archive0))
                luckyID.append({'id': mminer[0] + ':' + miner[0],
                                'num': str(block - block0)})

            j += 1
        i += 1
    if luckyID:
        for item in luckyID:
            print item['id'] + ' found ' + item['num'] + ' new block(s).'
    return (data, luckyID)
