.text
quicksort:
		addiu $sp, $sp, -4
		sw $fp, ($sp)
		move $fp, $sp
		sw $t0, -76($fp)
		sw $t1, -80($fp)
		sw $t2, -84($fp)
		sw $t3, -88($fp)
		sw $t4, -92($fp)
		sw $t5, -96($fp)
		sw $t6, -100($fp)
		sw $t7, -104($fp)
		sw $t8, -108($fp)
		sw $t9, -112($fp)
		sw $ra, -116($fp)
		addiu $sp, $fp, -116

		lw $t0, -48($fp)
		lw $t1, -44($fp)
		li $t1, 0
		li $t0, 0
		bge $a1, $a2, quicksort_end
		sw $t0, -48($fp)
		sw $t1, -44($fp)
		lw $t0, -24($fp)
		lw $t1, -56($fp)
		lw $t2, -20($fp)
		lw $t3, -44($fp)
		lw $t4, -60($fp)
		lw $t5, -48($fp)
		add $t1, $a1, $a2
		li $t2, 2
		div $t1, $t1, $t2
		move $t0, $t1
		sll $t0, $t0, 2
		addu $t0, $a0, $t0
		lw $t4, ($t0)
		addi $t3, $a1, -1
		addi $t5, $a2, 1
		sw $t0, -24($fp)
		sw $t1, -56($fp)
		sw $t2, -20($fp)
		sw $t3, -44($fp)
		sw $t4, -60($fp)
		sw $t5, -48($fp)
	quicksort_loop0:
	quicksort_loop1:
		lw $t0, -28($fp)
		lw $t1, -44($fp)
		lw $t2, -72($fp)
		lw $t3, -64($fp)
		lw $t4, -60($fp)
		addi $t1, $t1, 1
		move $t0, $t1
		sll $t0, $t0, 2
		addu $t0, $a0, $t0
		lw $t2, ($t0)
		move $t3, $t2
		blt $t3, $t4, quicksort_loop1
		sw $t0, -28($fp)
		sw $t1, -44($fp)
		sw $t2, -72($fp)
		sw $t3, -64($fp)
		sw $t4, -60($fp)
	quicksort_loop2:
		lw $t0, -32($fp)
		lw $t1, -72($fp)
		lw $t2, -48($fp)
		lw $t3, -68($fp)
		lw $t4, -60($fp)
		addi $t2, $t2, -1
		move $t0, $t2
		sll $t0, $t0, 2
		addu $t0, $a0, $t0
		lw $t1, ($t0)
		move $t3, $t1
		bgt $t3, $t4, quicksort_loop2
		sw $t0, -32($fp)
		sw $t1, -72($fp)
		sw $t2, -48($fp)
		sw $t3, -68($fp)
		sw $t4, -60($fp)
		lw $t0, -48($fp)
		lw $t1, -44($fp)
		bge $t1, $t0, quicksort_exit0
		sw $t0, -48($fp)
		sw $t1, -44($fp)
		lw $t0, -40($fp)
		lw $t1, -36($fp)
		lw $t2, -44($fp)
		lw $t3, -48($fp)
		lw $t4, -64($fp)
		lw $t5, -68($fp)
		move $t1, $t3
		sll $t1, $t1, 2
		addu $t1, $a0, $t1
		sw $t4, ($t1)
		move $t0, $t2
		sll $t0, $t0, 2
		addu $t0, $a0, $t0
		sw $t5, ($t0)
		j quicksort_loop0
		sw $t0, -40($fp)
		sw $t1, -36($fp)
		sw $t2, -44($fp)
		sw $t3, -48($fp)
		sw $t4, -64($fp)
		sw $t5, -68($fp)
	quicksort_exit0:
		lw $t0, -48($fp)
		lw $t1, -52($fp)
		addi $t1, $t0, 1
		sw $a0, -4($fp)
		sw $a1, -8($fp)
		sw $a2, -12($fp)
		move $a0, $a0
		move $a1, $a1
		move $a2, $t0
		jal quicksort
		lw $a0, -4($fp)
		lw $a1, -8($fp)
		lw $a2, -12($fp)
		addi $t0, $t0, 1
		sw $a0, -4($fp)
		sw $a1, -8($fp)
		sw $a2, -12($fp)
		move $a0, $a0
		move $a1, $t0
		move $a2, $a2
		jal quicksort
		lw $a0, -4($fp)
		lw $a1, -8($fp)
		lw $a2, -12($fp)
		sw $t0, -48($fp)
		sw $t1, -52($fp)
	quicksort_end:

		lw $ra, -116($fp)
		lw $t0, -76($fp)
		lw $t1, -80($fp)
		lw $t2, -84($fp)
		lw $t3, -88($fp)
		lw $t4, -92($fp)
		lw $t5, -96($fp)
		lw $t6, -100($fp)
		lw $t7, -104($fp)
		lw $t8, -108($fp)
		lw $t9, -112($fp)
		move $sp, $fp
		lw $fp, ($sp)
		addiu $sp, $sp, 4

		jr $ra
main:
		addiu $sp, $sp, -4
		sw $fp, ($sp)
		move $fp, $sp
		li $v0, 9
		li $a0, 400
		syscall
		sw $v0, -20($fp)
		sw $t0, -48($fp)
		sw $t1, -52($fp)
		sw $t2, -56($fp)
		sw $t3, -60($fp)
		sw $t4, -64($fp)
		sw $t5, -68($fp)
		sw $t6, -72($fp)
		sw $t7, -76($fp)
		sw $t8, -80($fp)
		sw $t9, -84($fp)
		addiu $sp, $fp, -84

		lw $t0, -24($fp)
		lw $t1, -40($fp)
		lw $t2, -44($fp)
		li $t2, 0
		li $v0, 5
		syscall
		move $t1, $v0
		li $t0, 100
		bgt $t1, $t0, main_return
		sw $t0, -24($fp)
		sw $t1, -40($fp)
		sw $t2, -44($fp)
		lw $t0, -40($fp)
		lw $t1, -36($fp)
		addi $t0, $t0, -1
		li $t1, 0
		sw $t0, -40($fp)
		sw $t1, -36($fp)
	main_loop0:
		lw $t0, -40($fp)
		lw $t1, -36($fp)
		bgt $t1, $t0, main_exit0
		sw $t0, -40($fp)
		sw $t1, -36($fp)
		lw $t0, -28($fp)
		lw $t1, -36($fp)
		lw $t2, -44($fp)
		lw $t3, -20($fp)
		li $v0, 5
		syscall
		move $t2, $v0
		move $t0, $t1
		sll $t0, $t0, 2
		addu $t0, $t3, $t0
		sw $t2, ($t0)
		addi $t1, $t1, 1
		j main_loop0
		sw $t0, -28($fp)
		sw $t1, -36($fp)
		sw $t2, -44($fp)
		sw $t3, -20($fp)
	main_exit0:
		lw $t0, -40($fp)
		lw $t1, -20($fp)
		lw $t2, -36($fp)
		sw $a0, -4($fp)
		sw $a1, -8($fp)
		sw $a2, -12($fp)
		move $a0, $t1
		li $a1, 0
		move $a2, $t0
		jal quicksort
		lw $a0, -4($fp)
		lw $a1, -8($fp)
		lw $a2, -12($fp)
		li $t2, 0
		sw $t0, -40($fp)
		sw $t1, -20($fp)
		sw $t2, -36($fp)
	main_loop1:
		lw $t0, -40($fp)
		lw $t1, -36($fp)
		bgt $t1, $t0, main_exit1
		sw $t0, -40($fp)
		sw $t1, -36($fp)
		lw $t0, -32($fp)
		lw $t1, -36($fp)
		lw $t2, -44($fp)
		lw $t3, -20($fp)
		move $t0, $t1
		sll $t0, $t0, 2
		addu $t0, $t3, $t0
		lw $t2, ($t0)
		sw $a0, -4($fp)
		move $a0, $t2
		li $v0, 1
		syscall
		lw $a0, -4($fp)
		sw $a0, -4($fp)
		li $a0, 10
		li $v0, 11
		syscall
		lw $a0, -4($fp)
		addi $t1, $t1, 1
		j main_loop1
		sw $t0, -32($fp)
		sw $t1, -36($fp)
		sw $t2, -44($fp)
		sw $t3, -20($fp)
	main_exit1:
	main_return:

		lw $t0, -48($fp)
		lw $t1, -52($fp)
		lw $t2, -56($fp)
		lw $t3, -60($fp)
		lw $t4, -64($fp)
		lw $t5, -68($fp)
		lw $t6, -72($fp)
		lw $t7, -76($fp)
		lw $t8, -80($fp)
		lw $t9, -84($fp)
		move $sp, $fp
		lw $fp, ($sp)
		addiu $sp, $sp, 4

		li $v0, 10
		syscall
