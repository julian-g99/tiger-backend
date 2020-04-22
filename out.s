.text
main:
	addiu $sp, $sp, -4
	sw $fp, ($sp)
	move $fp, $sp
	li $v0, 9
	li $a0, 400
	syscall
	addiu $sp, $sp, -4
	sw $v0, ($sp)
	li $v0, 9
	li $a0, 4000
	syscall
	addiu $sp, $sp, -4
	sw $v0, ($sp)
	li $v0, 9
	li $a0, 400
	syscall
	addiu $sp, $sp, -4
	sw $v0, ($sp)
	li $v0, 9
	li $a0, 400
	syscall
	addiu $sp, $sp, -4
	sw $v0, ($sp)
	sw $t0, -124($fp)
	sw $t1, -128($fp)
	sw $t2, -132($fp)
	sw $t3, -136($fp)
	sw $t4, -140($fp)
	sw $t5, -144($fp)
	sw $t6, -148($fp)
	sw $t7, -152($fp)
	addiu $sp, $fp, -156

	lw $t1, -20($fp)
	move $t0, $t1
	sw $t0, -92($fp)
	sw $t1, -20($fp)
	lw $t1, -92($fp)
	addi $t0, $t1, 100
	sw $t0, -96($fp)
	sw $t1, -92($fp)
	li $t0, 0
	sw $t0, -108($fp)
	main_CONVERT_ARRAY_ASSIGN_LOOP:
	lw $t0, -92($fp)
	lw $t1, -96($fp)
	bge $t0, $t1, main_CONVERT_ARRAY_ASSIGN_END
	sw $t0, -92($fp)
	sw $t1, -96($fp)
	lw $t0, -108($fp)
	lw $t1, -92($fp)
	sw $t0, ($t1)
	sw $t0, -108($fp)
	sw $t1, -92($fp)
	lw $t0, -92($fp)
	lw $t1, -92($fp)
	addi $t0, $t1, 4
	sw $t0, -92($fp)
	sw $t1, -92($fp)
	j main_CONVERT_ARRAY_ASSIGN_LOOP
	main_CONVERT_ARRAY_ASSIGN_END:
	li $t0, 10
	sw $t0, -60($fp)
	li $t0, 0
	sw $t0, -72($fp)
	li $v0, 5
	syscall
	move $t0, $v0
	sw $t0, -64($fp)
	li $t0, 0
	sw $t0, -44($fp)
	main_L0:
	lw $t0, -44($fp)
	lw $t1, -64($fp)
	bge $t0, $t1, main_EOI
	sw $t0, -44($fp)
	sw $t1, -64($fp)
	li $v0, 5
	syscall
	move $t0, $v0
	sw $t0, -40($fp)
	lw $t0, -28($fp)
	lw $t1, -28($fp)
	lw $t2, -44($fp)
	add $t0, $t1, $t2
	sw $t0, -28($fp)
	sw $t1, -28($fp)
	sw $t2, -44($fp)
	lw $t0, -40($fp)
	lw $t1, -28($fp)
	sw $t0, ($t1)
	sw $t0, -40($fp)
	sw $t1, -28($fp)
	lw $t0, -28($fp)
	lw $t1, -28($fp)
	lw $t2, -44($fp)
	sub $t0, $t1, $t2
	sw $t0, -28($fp)
	sw $t1, -28($fp)
	sw $t2, -44($fp)
	li $t0, 0
	sw $t0, -52($fp)
	main_L1:
	lw $t0, -52($fp)
	lw $t1, -40($fp)
	bge $t0, $t1, main_L2
	sw $t0, -52($fp)
	sw $t1, -40($fp)
	li $v0, 5
	syscall
	move $t0, $v0
	sw $t0, -88($fp)
	lw $t1, -60($fp)
	lw $t2, -44($fp)
	mul $t0, $t1, $t2
	sw $t0, -76($fp)
	sw $t1, -60($fp)
	sw $t2, -44($fp)
	lw $t0, -76($fp)
	lw $t1, -76($fp)
	lw $t2, -52($fp)
	add $t0, $t1, $t2
	sw $t0, -76($fp)
	sw $t1, -76($fp)
	sw $t2, -52($fp)
	lw $t0, -24($fp)
	lw $t1, -24($fp)
	lw $t2, -76($fp)
	add $t0, $t1, $t2
	sw $t0, -24($fp)
	sw $t1, -24($fp)
	sw $t2, -76($fp)
	lw $t0, -88($fp)
	lw $t1, -24($fp)
	sw $t0, ($t1)
	sw $t0, -88($fp)
	sw $t1, -24($fp)
	lw $t0, -24($fp)
	lw $t1, -24($fp)
	lw $t2, -76($fp)
	sub $t0, $t1, $t2
	sw $t0, -24($fp)
	sw $t1, -24($fp)
	sw $t2, -76($fp)
	lw $t0, -52($fp)
	lw $t1, -52($fp)
	addi $t0, $t1, 1
	sw $t0, -52($fp)
	sw $t1, -52($fp)
	j main_L1
	main_L2:
	lw $t0, -44($fp)
	lw $t1, -44($fp)
	addi $t0, $t1, 1
	sw $t0, -44($fp)
	sw $t1, -44($fp)
	j main_L0
	main_EOI:
	addi $t0, $0, 1
	sw $t0, -112($fp)
	lw $t0, -112($fp)
	lw $t1, -20($fp)
	sw $t0, 0($t1)
	sw $t0, -112($fp)
	sw $t1, -20($fp)
	addi $t0, $0, 0
	sw $t0, -116($fp)
	lw $t0, -116($fp)
	lw $t1, -32($fp)
	sw $t0, 0($t1)
	sw $t0, -116($fp)
	sw $t1, -32($fp)
	lw $t0, -80($fp)
	lw $t1, -20($fp)
	lw $t0, 0($t1)
	sw $t0, -80($fp)
	sw $t1, -20($fp)
	li $t0, 0
	sw $t0, -48($fp)
	lw $t1, -48($fp)
	move $t0, $t1
	sw $t0, -44($fp)
	sw $t1, -48($fp)
	li $t0, 1
	sw $t0, -52($fp)
	main_L3:
	lw $t0, -44($fp)
	lw $t1, -52($fp)
	beq $t0, $t1, main_FIN
	sw $t0, -44($fp)
	sw $t1, -52($fp)
	lw $t0, -32($fp)
	lw $t1, -32($fp)
	lw $t2, -44($fp)
	add $t0, $t1, $t2
	sw $t0, -32($fp)
	sw $t1, -32($fp)
	sw $t2, -44($fp)
	lw $t0, -68($fp)
	lw $t1, -32($fp)
	lw $t0, ($t1)
	sw $t0, -68($fp)
	sw $t1, -32($fp)
	lw $t0, -32($fp)
	lw $t1, -32($fp)
	lw $t2, -44($fp)
	sub $t0, $t1, $t2
	sw $t0, -32($fp)
	sw $t1, -32($fp)
	sw $t2, -44($fp)
	lw $t1, -44($fp)
	addi $t0, $t1, 1
	sw $t0, -48($fp)
	sw $t1, -44($fp)
	lw $t1, -48($fp)
	move $t0, $t1
	sw $t0, -44($fp)
	sw $t1, -48($fp)
	lw $t0, -28($fp)
	lw $t1, -28($fp)
	lw $t2, -68($fp)
	add $t0, $t1, $t2
	sw $t0, -28($fp)
	sw $t1, -28($fp)
	sw $t2, -68($fp)
	lw $t0, -40($fp)
	lw $t1, -28($fp)
	lw $t0, ($t1)
	sw $t0, -40($fp)
	sw $t1, -28($fp)
	lw $t0, -28($fp)
	lw $t1, -28($fp)
	lw $t2, -68($fp)
	sub $t0, $t1, $t2
	sw $t0, -28($fp)
	sw $t1, -28($fp)
	sw $t2, -68($fp)
	lw $t1, -44($fp)
	move $t0, $t1
	sw $t0, -56($fp)
	sw $t1, -44($fp)
	li $t0, 0
	sw $t0, -56($fp)
	main_L4:
	lw $t0, -56($fp)
	lw $t1, -40($fp)
	bge $t0, $t1, main_L5
	sw $t0, -56($fp)
	sw $t1, -40($fp)
	lw $t1, -56($fp)
	move $t0, $t1
	sw $t0, -76($fp)
	sw $t1, -56($fp)
	lw $t1, -60($fp)
	lw $t2, -68($fp)
	mul $t0, $t1, $t2
	sw $t0, -76($fp)
	sw $t1, -60($fp)
	sw $t2, -68($fp)
	lw $t0, -76($fp)
	lw $t1, -76($fp)
	lw $t2, -56($fp)
	add $t0, $t1, $t2
	sw $t0, -76($fp)
	sw $t1, -76($fp)
	sw $t2, -56($fp)
	lw $t0, -24($fp)
	lw $t1, -24($fp)
	lw $t2, -76($fp)
	add $t0, $t1, $t2
	sw $t0, -24($fp)
	sw $t1, -24($fp)
	sw $t2, -76($fp)
	lw $t0, -88($fp)
	lw $t1, -24($fp)
	lw $t0, ($t1)
	sw $t0, -88($fp)
	sw $t1, -24($fp)
	lw $t0, -24($fp)
	lw $t1, -24($fp)
	lw $t2, -76($fp)
	sub $t0, $t1, $t2
	sw $t0, -24($fp)
	sw $t1, -24($fp)
	sw $t2, -76($fp)
	lw $t0, -20($fp)
	lw $t1, -20($fp)
	lw $t2, -88($fp)
	add $t0, $t1, $t2
	sw $t0, -20($fp)
	sw $t1, -20($fp)
	sw $t2, -88($fp)
	lw $t0, -84($fp)
	lw $t1, -20($fp)
	lw $t0, ($t1)
	sw $t0, -84($fp)
	sw $t1, -20($fp)
	lw $t0, -20($fp)
	lw $t1, -20($fp)
	lw $t2, -88($fp)
	sub $t0, $t1, $t2
	sw $t0, -20($fp)
	sw $t1, -20($fp)
	sw $t2, -88($fp)
	li $t0, 1
	sw $t0, -120($fp)
	lw $t0, -84($fp)
	lw $t1, -120($fp)
	beq $t0, $t1, main_L6
	sw $t0, -84($fp)
	sw $t1, -120($fp)
	addi $t0, 1
	sw $t0, -100($fp)
	lw $t0, -20($fp)
	lw $t1, -20($fp)
	lw $t2, -88($fp)
	add $t0, $t1, $t2
	sw $t0, -20($fp)
	sw $t1, -20($fp)
	sw $t2, -88($fp)
	lw $t0, -104($fp)
	lw $t1, -20($fp)
	sw $t0, ($t1)
	sw $t0, -104($fp)
	sw $t1, -20($fp)
	lw $t0, -20($fp)
	lw $t1, -20($fp)
	lw $t2, -88($fp)
	sub $t0, $t1, $t2
	sw $t0, -20($fp)
	sw $t1, -20($fp)
	sw $t2, -88($fp)
	lw $t0, -32($fp)
	lw $t1, -32($fp)
	lw $t2, -52($fp)
	add $t0, $t1, $t2
	sw $t0, -32($fp)
	sw $t1, -32($fp)
	sw $t2, -52($fp)
	lw $t0, -88($fp)
	lw $t1, -32($fp)
	sw $t0, ($t1)
	sw $t0, -88($fp)
	sw $t1, -32($fp)
	lw $t0, -32($fp)
	lw $t1, -32($fp)
	lw $t2, -52($fp)
	sub $t0, $t1, $t2
	sw $t0, -32($fp)
	sw $t1, -32($fp)
	sw $t2, -52($fp)
	lw $t0, -20($fp)
	lw $t1, -20($fp)
	lw $t2, -88($fp)
	add $t0, $t1, $t2
	sw $t0, -20($fp)
	sw $t1, -20($fp)
	sw $t2, -88($fp)
	lw $t0, -80($fp)
	lw $t1, -20($fp)
	lw $t0, ($t1)
	sw $t0, -80($fp)
	sw $t1, -20($fp)
	lw $t0, -20($fp)
	lw $t1, -20($fp)
	lw $t2, -88($fp)
	sub $t0, $t1, $t2
	sw $t0, -20($fp)
	sw $t1, -20($fp)
	sw $t2, -88($fp)
	lw $t0, -52($fp)
	lw $t1, -52($fp)
	addi $t0, $t1, 1
	sw $t0, -52($fp)
	sw $t1, -52($fp)
	main_L6:
	lw $t0, -56($fp)
	lw $t1, -56($fp)
	addi $t0, $t1, 1
	sw $t0, -56($fp)
	sw $t1, -56($fp)
	j main_L4
	main_L5:
	j main_L3
	main_FIN:
	li $t0, 0
	sw $t0, -48($fp)
	lw $t1, -48($fp)
	move $t0, $t1
	sw $t0, -44($fp)
	sw $t1, -48($fp)
	main_L7:
	lw $t0, -44($fp)
	lw $t1, -52($fp)
	beq $t0, $t1, main_L8
	sw $t0, -44($fp)
	sw $t1, -52($fp)
	lw $t0, -32($fp)
	lw $t1, -32($fp)
	lw $t2, -44($fp)
	add $t0, $t1, $t2
	sw $t0, -32($fp)
	sw $t1, -32($fp)
	sw $t2, -44($fp)
	lw $t0, -88($fp)
	lw $t1, -32($fp)
	lw $t0, ($t1)
	sw $t0, -88($fp)
	sw $t1, -32($fp)
	lw $t0, -32($fp)
	lw $t1, -32($fp)
	lw $t2, -44($fp)
	sub $t0, $t1, $t2
	sw $t0, -32($fp)
	sw $t1, -32($fp)
	sw $t2, -44($fp)
	lw $t0, -88($fp)
	move $a0, $t0
	sw $t0, -88($fp)
	li $v0, 1
	syscall
	li $a0, 10
	li $v0, 11
	syscall
	lw $t1, -44($fp)
	addi $t0, $t1, 1
	sw $t0, -48($fp)
	sw $t1, -44($fp)
	lw $t1, -48($fp)
	move $t0, $t1
	sw $t0, -44($fp)
	sw $t1, -48($fp)
	j main_L7
	main_L8:

	lw $t0, -124($fp)
	lw $t1, -128($fp)
	lw $t2, -132($fp)
	lw $t3, -136($fp)
	lw $t4, -140($fp)
	lw $t5, -144($fp)
	lw $t6, -148($fp)
	lw $t7, -152($fp)
	move $sp, $fp
	lw $fp, ($sp)
	addiu $sp, $sp, 4

	li $v0, 10
	syscall
