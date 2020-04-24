.text
main:
		addiu $sp, $sp, -4
		sw $fp, ($sp)
		move $fp, $sp
		li $v0, 9
		li $a0, 400
		syscall
		sw $v0, -20($fp)
		li $v0, 9
		li $a0, 4000
		syscall
		sw $v0, -24($fp)
		li $v0, 9
		li $a0, 400
		syscall
		sw $v0, -28($fp)
		li $v0, 9
		li $a0, 400
		syscall
		sw $v0, -32($fp)
		sw $t0, -156($fp)
		sw $t1, -160($fp)
		sw $t2, -164($fp)
		sw $t3, -168($fp)
		sw $t4, -172($fp)
		sw $t5, -176($fp)
		sw $t6, -180($fp)
		sw $t7, -184($fp)
		sw $t8, -188($fp)
		sw $t9, -192($fp)
		addiu $sp, $fp, -196

		li $t0, 100
		sw $t0, -40($fp)
		lw $t1, -20($fp)
		move $t0, $t1
		sw $t0, -44($fp)
		sw $t1, -20($fp)
		li $t0, 0
		sw $t0, -84($fp)
	main_array_assign_loop0:
		lw $t0, -40($fp)
		blez $t0, main_array_assign_end0
		sw $t0, -40($fp)
		lw $t0, -84($fp)
		lw $t1, -44($fp)
		sw $t0, ($t1)
		sw $t0, -84($fp)
		sw $t1, -44($fp)
		lw $t0, -40($fp)
		addi $t0, $t0, -1
		sw $t0, -40($fp)
		lw $t0, -44($fp)
		addiu $t0, $t0, 4
		sw $t0, -44($fp)
		j main_array_assign_loop0
	main_array_assign_end0:
		li $t0, 10
		sw $t0, -124($fp)
		li $t0, 0
		sw $t0, -136($fp)
		li $v0, 5
		syscall
		move $t0, $v0
		sw $t0, -128($fp)
		li $t0, 0
		sw $t0, -108($fp)
	main_L0:
		lw $t0, -108($fp)
		lw $t1, -128($fp)
		bge $t0, $t1, main_EOI
		sw $t0, -108($fp)
		sw $t1, -128($fp)
		li $v0, 5
		syscall
		move $t0, $v0
		sw $t0, -36($fp)
		lw $t1, -108($fp)
		move $t0, $t1
		sw $t0, -92($fp)
		sw $t1, -108($fp)
		lw $t0, -92($fp)
		sll $t0, $t0, 2
		sw $t0, -92($fp)
		lw $t0, -92($fp)
		lw $t1, -28($fp)
		addu $t0, $t1, $t0
		sw $t0, -92($fp)
		sw $t1, -28($fp)
		lw $t0, -36($fp)
		lw $t1, -92($fp)
		sw $t0, ($t1)
		sw $t0, -36($fp)
		sw $t1, -92($fp)
		li $t0, 0
		sw $t0, -116($fp)
	main_L1:
		lw $t0, -116($fp)
		lw $t1, -36($fp)
		bge $t0, $t1, main_L2
		sw $t0, -116($fp)
		sw $t1, -36($fp)
		li $v0, 5
		syscall
		move $t0, $v0
		sw $t0, -152($fp)
		lw $t1, -124($fp)
		lw $t2, -108($fp)
		mul $t0, $t1, $t2
		sw $t0, -140($fp)
		sw $t1, -124($fp)
		sw $t2, -108($fp)
		lw $t0, -140($fp)
		lw $t1, -116($fp)
		add $t0, $t0, $t1
		sw $t0, -140($fp)
		sw $t1, -116($fp)
		lw $t1, -140($fp)
		move $t0, $t1
		sw $t0, -96($fp)
		sw $t1, -140($fp)
		lw $t0, -96($fp)
		sll $t0, $t0, 2
		sw $t0, -96($fp)
		lw $t0, -96($fp)
		lw $t1, -24($fp)
		addu $t0, $t1, $t0
		sw $t0, -96($fp)
		sw $t1, -24($fp)
		lw $t0, -152($fp)
		lw $t1, -96($fp)
		sw $t0, ($t1)
		sw $t0, -152($fp)
		sw $t1, -96($fp)
		lw $t0, -116($fp)
		addi $t0, $t0, 1
		sw $t0, -116($fp)
		j main_L1
	main_L2:
		lw $t0, -108($fp)
		addi $t0, $t0, 1
		sw $t0, -108($fp)
		j main_L0
	main_EOI:
		li $t0, 1
		sw $t0, -100($fp)
		lw $t0, -100($fp)
		lw $t1, -20($fp)
		sw $t0, ($t1)
		sw $t0, -100($fp)
		sw $t1, -20($fp)
		li $t0, 0
		sw $t0, -104($fp)
		lw $t0, -104($fp)
		lw $t1, -32($fp)
		sw $t0, ($t1)
		sw $t0, -104($fp)
		sw $t1, -32($fp)
		lw $t0, -144($fp)
		lw $t1, -20($fp)
		lw $t0, ($t1)
		sw $t0, -144($fp)
		sw $t1, -20($fp)
		li $t0, 0
		sw $t0, -112($fp)
		lw $t1, -112($fp)
		move $t0, $t1
		sw $t0, -108($fp)
		sw $t1, -112($fp)
		li $t0, 1
		sw $t0, -116($fp)
	main_L3:
		lw $t0, -108($fp)
		lw $t1, -116($fp)
		beq $t0, $t1, main_FIN
		sw $t0, -108($fp)
		sw $t1, -116($fp)
		lw $t1, -108($fp)
		move $t0, $t1
		sw $t0, -48($fp)
		sw $t1, -108($fp)
		lw $t0, -48($fp)
		sll $t0, $t0, 2
		sw $t0, -48($fp)
		lw $t0, -48($fp)
		lw $t1, -32($fp)
		addu $t0, $t1, $t0
		sw $t0, -48($fp)
		sw $t1, -32($fp)
		lw $t0, -132($fp)
		lw $t1, -48($fp)
		lw $t0, ($t1)
		sw $t0, -132($fp)
		sw $t1, -48($fp)
		lw $t1, -108($fp)
		addi $t0, $t1, 1
		sw $t0, -112($fp)
		sw $t1, -108($fp)
		lw $t1, -112($fp)
		move $t0, $t1
		sw $t0, -108($fp)
		sw $t1, -112($fp)
		lw $t1, -132($fp)
		move $t0, $t1
		sw $t0, -52($fp)
		sw $t1, -132($fp)
		lw $t0, -52($fp)
		sll $t0, $t0, 2
		sw $t0, -52($fp)
		lw $t0, -52($fp)
		lw $t1, -28($fp)
		addu $t0, $t1, $t0
		sw $t0, -52($fp)
		sw $t1, -28($fp)
		lw $t0, -36($fp)
		lw $t1, -52($fp)
		lw $t0, ($t1)
		sw $t0, -36($fp)
		sw $t1, -52($fp)
		lw $t1, -108($fp)
		move $t0, $t1
		sw $t0, -120($fp)
		sw $t1, -108($fp)
		li $t0, 0
		sw $t0, -120($fp)
	main_L4:
		lw $t0, -120($fp)
		lw $t1, -36($fp)
		bge $t0, $t1, main_L5
		sw $t0, -120($fp)
		sw $t1, -36($fp)
		lw $t1, -120($fp)
		move $t0, $t1
		sw $t0, -140($fp)
		sw $t1, -120($fp)
		lw $t1, -124($fp)
		lw $t2, -132($fp)
		mul $t0, $t1, $t2
		sw $t0, -140($fp)
		sw $t1, -124($fp)
		sw $t2, -132($fp)
		lw $t0, -140($fp)
		lw $t1, -120($fp)
		add $t0, $t0, $t1
		sw $t0, -140($fp)
		sw $t1, -120($fp)
		lw $t1, -140($fp)
		move $t0, $t1
		sw $t0, -56($fp)
		sw $t1, -140($fp)
		lw $t0, -56($fp)
		sll $t0, $t0, 2
		sw $t0, -56($fp)
		lw $t0, -56($fp)
		lw $t1, -24($fp)
		addu $t0, $t1, $t0
		sw $t0, -56($fp)
		sw $t1, -24($fp)
		lw $t0, -152($fp)
		lw $t1, -56($fp)
		lw $t0, ($t1)
		sw $t0, -152($fp)
		sw $t1, -56($fp)
		lw $t1, -152($fp)
		move $t0, $t1
		sw $t0, -60($fp)
		sw $t1, -152($fp)
		lw $t0, -60($fp)
		sll $t0, $t0, 2
		sw $t0, -60($fp)
		lw $t0, -60($fp)
		lw $t1, -20($fp)
		addu $t0, $t1, $t0
		sw $t0, -60($fp)
		sw $t1, -20($fp)
		lw $t0, -148($fp)
		lw $t1, -60($fp)
		lw $t0, ($t1)
		sw $t0, -148($fp)
		sw $t1, -60($fp)
		li $t0, 1
		sw $t0, -64($fp)
		lw $t0, -148($fp)
		lw $t1, -64($fp)
		beq $t0, $t1, main_L6
		sw $t0, -148($fp)
		sw $t1, -64($fp)
		li $t0, 1
		sw $t0, -68($fp)
		lw $t1, -152($fp)
		move $t0, $t1
		sw $t0, -72($fp)
		sw $t1, -152($fp)
		lw $t0, -72($fp)
		sll $t0, $t0, 2
		sw $t0, -72($fp)
		lw $t0, -72($fp)
		lw $t1, -20($fp)
		addu $t0, $t1, $t0
		sw $t0, -72($fp)
		sw $t1, -20($fp)
		lw $t0, -68($fp)
		lw $t1, -72($fp)
		sw $t0, ($t1)
		sw $t0, -68($fp)
		sw $t1, -72($fp)
		lw $t1, -116($fp)
		move $t0, $t1
		sw $t0, -76($fp)
		sw $t1, -116($fp)
		lw $t0, -76($fp)
		sll $t0, $t0, 2
		sw $t0, -76($fp)
		lw $t0, -76($fp)
		lw $t1, -32($fp)
		addu $t0, $t1, $t0
		sw $t0, -76($fp)
		sw $t1, -32($fp)
		lw $t0, -152($fp)
		lw $t1, -76($fp)
		sw $t0, ($t1)
		sw $t0, -152($fp)
		sw $t1, -76($fp)
		lw $t1, -152($fp)
		move $t0, $t1
		sw $t0, -80($fp)
		sw $t1, -152($fp)
		lw $t0, -80($fp)
		sll $t0, $t0, 2
		sw $t0, -80($fp)
		lw $t0, -80($fp)
		lw $t1, -20($fp)
		addu $t0, $t1, $t0
		sw $t0, -80($fp)
		sw $t1, -20($fp)
		lw $t0, -144($fp)
		lw $t1, -80($fp)
		lw $t0, ($t1)
		sw $t0, -144($fp)
		sw $t1, -80($fp)
		lw $t0, -116($fp)
		addi $t0, $t0, 1
		sw $t0, -116($fp)
	main_L6:
		lw $t0, -120($fp)
		addi $t0, $t0, 1
		sw $t0, -120($fp)
		j main_L4
	main_L5:
		j main_L3
	main_FIN:
		li $t0, 0
		sw $t0, -112($fp)
		lw $t1, -112($fp)
		move $t0, $t1
		sw $t0, -108($fp)
		sw $t1, -112($fp)
	main_L7:
		lw $t0, -108($fp)
		lw $t1, -116($fp)
		beq $t0, $t1, main_L8
		sw $t0, -108($fp)
		sw $t1, -116($fp)
		lw $t1, -108($fp)
		move $t0, $t1
		sw $t0, -88($fp)
		sw $t1, -108($fp)
		lw $t0, -88($fp)
		sll $t0, $t0, 2
		sw $t0, -88($fp)
		lw $t0, -88($fp)
		lw $t1, -32($fp)
		addu $t0, $t1, $t0
		sw $t0, -88($fp)
		sw $t1, -32($fp)
		lw $t0, -152($fp)
		lw $t1, -88($fp)
		lw $t0, ($t1)
		sw $t0, -152($fp)
		sw $t1, -88($fp)
		sw $a0, -4($fp)
		lw $t0, -152($fp)
		move $a0, $t0
		sw $t0, -152($fp)
		li $v0, 1
		syscall
		lw $a0, -4($fp)
		sw $a0, -4($fp)
		li $a0, 10
		li $v0, 11
		syscall
		lw $a0, -4($fp)
		lw $t1, -108($fp)
		addi $t0, $t1, 1
		sw $t0, -112($fp)
		sw $t1, -108($fp)
		lw $t1, -112($fp)
		move $t0, $t1
		sw $t0, -108($fp)
		sw $t1, -112($fp)
		j main_L7
	main_L8:

		lw $t0, -156($fp)
		lw $t1, -160($fp)
		lw $t2, -164($fp)
		lw $t3, -168($fp)
		lw $t4, -172($fp)
		lw $t5, -176($fp)
		lw $t6, -180($fp)
		lw $t7, -184($fp)
		lw $t8, -188($fp)
		lw $t9, -192($fp)
		move $sp, $fp
		lw $fp, ($sp)
		addiu $sp, $sp, 4

		li $v0, 10
		syscall
