.text
main:
	addiu $sp, $sp, -4
	sw $fp, ($sp)
	move $fp, $sp
	addiu $sp, $sp, -4
	addiu $sp, $sp, -4
	addiu $sp, $sp, -4
	addiu $sp, $sp, -4
	addiu $sp, $sp, -4
	addiu $sp, $sp, -4
	addiu $sp, $sp, -4
	sw $t0, ($sp)
	addiu $sp, $sp, -4
	sw $t1, ($sp)
	addiu $sp, $sp, -4
	sw $t2, ($sp)
	addiu $sp, $sp, -4
	sw $t3, ($sp)
	addiu $sp, $sp, -4
	sw $t4, ($sp)
	addiu $sp, $sp, -4
	sw $t5, ($sp)
	addiu $sp, $sp, -4
	sw $t6, ($sp)
	addiu $sp, $sp, -4
	sw $t7, ($sp)


    # callr, x, geti
    addiu $sp, $sp, -4
	li $v0, 5
	syscall

	sw $t0, -28($fp)
	lw $t0, -20($fp)
	move $t0, $v0
	sw $t0, -20($fp)
	lw $t0, -28($fp)

    # callr, z, fib, x
	sw $a0, -4($fp)
	sw $t0, -28($fp)
	lw $t0, -20($fp)
	move $a0, $t0
	sw $t0, -20($fp)
	lw $t0, -28($fp)

	jal fib
    lw $a0, -4($fp) # again, moved
	sw $t0, -28($fp)
	lw $t0, -24($fp)
	move $t0, $v0
	sw $t0, -24($fp)
	lw $t0, -28($fp)

    # assign, x, z
    sw $t0, -28($fp)
    lw $t0, -20($fp)
    sw $t1, -32($fp)
    lw $t1, -24($fp)
    move $t0, $t1
    sw $t0, -20($fp)
    lw $t0, -28($fp)
    sw $t1, -24($fp)
    lw $t1, -32($fp)

    # call, puti, x
	sw $t0, -28($fp)
	lw $t0, -20($fp)
	move $a0, $t0
	sw $t0, -20($fp)
	lw $t0, -28($fp)

	li $v0, 1
	syscall

    # call, putc, 10
	li $a0, 10
	li $v0, 11
	syscall

    # epilogue
	lw $t0, -28($fp)
	lw $t1, -32($fp)
	lw $t2, -36($fp)
	lw $t3, -40($fp)
	lw $t4, -44($fp)
	lw $t5, -48($fp)
	lw $t6, -52($fp)
	lw $t7, -56($fp)
	move $sp, $fp
	lw $fp, ($sp)
	addiu $sp, $sp, 4

	li $v0, 10
	syscall


fib:
    # saving the fp
	addiu $sp, $sp, -4
	sw $fp, ($sp)
	move $fp, $sp

    # making space for arg registers
	addiu $sp, $sp, -4
	addiu $sp, $sp, -4
	addiu $sp, $sp, -4
	addiu $sp, $sp, -4

    # making space for local variables
	addiu $sp, $sp, -4
	addiu $sp, $sp, -4
	addiu $sp, $sp, -4
	addiu $sp, $sp, -4
	addiu $sp, $sp, -4
	addiu $sp, $sp, -4
	addiu $sp, $sp, -4
	addiu $sp, $sp, -4
	addiu $sp, $sp, -4

    # saving temp registers
	addiu $sp, $sp, -4
	sw $t0, ($sp)
	addiu $sp, $sp, -4
	sw $t1, ($sp)
	addiu $sp, $sp, -4
	sw $t2, ($sp)
	addiu $sp, $sp, -4
	sw $t3, ($sp)
	addiu $sp, $sp, -4
	sw $t4, ($sp)
	addiu $sp, $sp, -4
	sw $t5, ($sp)
	addiu $sp, $sp, -4
	sw $t6, ($sp)
	addiu $sp, $sp, -4
	sw $t7, ($sp)

    # padding
	addiu $sp, $sp, -4

    # saving ra
	addiu $sp, $sp, -4
	sw $ra, ($sp)


    # body

    # assign, t0, 0
	sw $t0, -56($fp)
	lw $t0, -32($fp)
	li $t0, 0
	sw $t0, -32($fp)
	lw $t0, -56($fp)

    # assign, r, 1
	sw $t0, -56($fp)
	lw $t0, -24($fp)
	li $t0, 1
	sw $t0, -24($fp)
	lw $t0, -56($fp)

    # assign, rr, r
	sw $t0, -56($fp)
	lw $t0, -28($fp)
	sw $t1, -60($fp)
	lw $t1, -24($fp)
	move $t0, $t1
	sw $t0, -28($fp)
	lw $t0, -56($fp)
	sw $t1, -24($fp)
	lw $t1, -60($fp)

    # brgt, if_label0, n, 1
	sw $t0, -56($fp)
	lw $t0, -52($fp)
	li $t0, 1
	sw $t0, -52($fp)
	lw $t0, -56($fp)

	sw $t0, -56($fp)
	lw $t0, -52($fp)
	bgt $a0, $t0, if_label0
	sw $t0, -52($fp)
	lw $t0, -56($fp)

    # assgin, t00, 0
	sw $t0, -56($fp)
	lw $t0, -36($fp)
	li $t0, 0
	sw $t0, -36($fp)
	lw $t0, -56($fp)

    # assign, r, n
	sw $t0, -56($fp)
	lw $t0, -24($fp)
	move $t0, $a0
	sw $t0, -24($fp)
	lw $t0, -56($fp)

    # assign, rr, r
	sw $t0, -56($fp)
	lw $t0, -28($fp)
	sw $t1, -60($fp)
	lw $t1, -24($fp)
	move $t0, $t1
	sw $t0, -28($fp)
	lw $t0, -56($fp)
	sw $t1, -24($fp)
	lw $t1, -60($fp)

    # goto, end
	j end

    # if_label0:
	if_label0:

    # sub, n, n, 1
	addi $a0, $a0, -1

    # callr, t1, fib, n
	sw $a0, -4($fp)
	move $a0, $a0
	jal fib
    lw $a0, -4($fp) # this was moved down here, was before the jal
	sw $t0, -56($fp)
	lw $t0, -40($fp)
	move $t0, $v0
	sw $t0, -40($fp)
	lw $t0, -56($fp)

    # sub, x, n, 1
	sw $t0, -56($fp)
	lw $t0, -48($fp)
	addi $t0, $a0, -1
	sw $t0, -48($fp)
	lw $t0, -56($fp)

    # sub, n, n, 1
	addi $a0, $a0, -1

    # callr, t2, fib, x
	sw $a0, -4($fp)
	sw $t0, -56($fp)
	lw $t0, -48($fp)
	move $a0, $t0
	sw $t0, -48($fp)
	lw $t0, -56($fp)
	jal fib
    lw $a0, -4($fp) # again, used to be before the jal
	sw $t0, -56($fp)
	lw $t0, -44($fp)
	move $t0, $v0
	sw $t0, -44($fp)
	lw $t0, -56($fp)

    # assign, t00, t0
	sw $t0, -56($fp)
	lw $t0, -36($fp)
	sw $t1, -60($fp)
	lw $t1, -32($fp)
	move $t0, $t1
	sw $t0, -36($fp)
	lw $t0, -56($fp)
	sw $t1, -32($fp)
	lw $t1, -60($fp)

    # assign, r, t0
	sw $t0, -56($fp)
	lw $t0, -24($fp)
	sw $t1, -60($fp)
	lw $t1, -32($fp)
	move $t0, $t1
	sw $t0, -24($fp)
	lw $t0, -56($fp)
	sw $t1, -32($fp)
	lw $t1, -60($fp)

    # add, r, t1, t2
	sw $t0, -56($fp)
	lw $t0, -24($fp)
	sw $t1, -60($fp)
	lw $t1, -40($fp)
	sw $t2, -64($fp)
	lw $t2, -44($fp)
	add $t0, $t1, $t2
	sw $t0, -24($fp)
	lw $t0, -56($fp)
	sw $t1, -40($fp)
	lw $t1, -60($fp)
	sw $t2, -44($fp)
	lw $t2, -64($fp)

    # assign, rr, r
	sw $t0, -56($fp)
	lw $t0, -28($fp)
	sw $t1, -60($fp)
	lw $t1, -24($fp)
	move $t0, $t1
	sw $t0, -28($fp)
	lw $t0, -56($fp)
	sw $t1, -24($fp)
	lw $t1, -60($fp)

    #end: 
	end:

    # return, rr
	sw $t0, -56($fp)
	lw $t0, -28($fp)
	move $v0, $t0
	sw $t0, -28($fp)
	lw $t0, -56($fp)

	lw $ra, -92($fp)
	lw $t0, -56($fp)
	lw $t1, -60($fp)
	lw $t2, -64($fp)
	lw $t3, -68($fp)
	lw $t4, -72($fp)
	lw $t5, -76($fp)
	lw $t6, -80($fp)
	lw $t7, -84($fp)
	move $sp, $fp
	lw $fp, ($sp)
	addiu $sp, $sp, 4

	jr $ra
