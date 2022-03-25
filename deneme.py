def calculateSeq(buffer,expected_seq_num) -> int :
    try:
        if(buffer[expected_seq_num]) : # if it is buffered find next necessary packet
            expected_seq_num +=1
            expected_seq_num = calculateSeq(buffer,expected_seq_num)
            return expected_seq_num
        return expected_seq_num

    except IndexError:
        return 



buffer = [None]*38
buffer[0] = 1
buffer[1] = 1
buffer[2] = 1
expected_seq_num = 1

expected_seq_num = calculateSeq(buffer,expected_seq_num)

a=5