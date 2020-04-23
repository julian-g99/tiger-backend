main:
addi $t1, $zero, 0
addi $t2, $t1, 10
loop1:
addi $t1, $zero, 0
beq $t2, $t1, endloop1
addi $t1, $zero, 1
sub $t2, $t2, $t1
endloop1:
addi $t1, $zero, 0
addi $t3, $t1, 3
addi $sp, $sp, -4
sw $t3, 0($sp)
addi $sp, $sp, -4
addi $t1, $zero, 10
sw $t1, 0($sp)
addi $sp, $sp, -4
jal func1
lw $t0, 0($sp)
addi $sp, $sp, 12
addi $sp, $sp, -4
sw $t0, 0($sp)
addi $sp, $sp, -4
jal func2
lw $t0, 0($sp)
addi $sp, $sp, 8
li $v0, 1
move $a0, $t0
syscall
li $v0, 10
syscall
func1:
addi $sp, $sp, -32
sw $s0, 0($sp)
sw $s1, 4($sp)
sw $s2, 8($sp)
sw $s3, 12($sp)
sw $s4, 16($sp)
sw $s5, 20($sp)
sw $s6, 24($sp)
sw $s7, 28($sp)
addi $sp, $sp, -4
sw $fp, 0($sp)
addi $sp, $sp, -4
sw $ra, 0($sp)
lw $t0, 48($sp)
lw $t1, 44($sp)
add $t2, $t0, $t1
lw $ra, 0($sp)
addi $sp, $sp, 4
lw $fp, 0($sp)
addi $sp, $sp, 4
addi $sp, $sp, 32
lw $s7, 0($sp)
lw $s6, -4($sp)
lw $s5, -8($sp)
lw $s4, -12($sp)
lw $s3, -16($sp)
lw $s2, -20($sp)
lw $s1, -24($sp)
lw $s0, -28($sp)
sw $t2, 0($sp)
jr $ra
func2:
addi $sp, $sp, -32
sw $s0, 0($sp)
sw $s1, 4($sp)
sw $s2, 8($sp)
sw $s3, 12($sp)
sw $s4, 16($sp)
sw $s5, 20($sp)
sw $s6, 24($sp)
sw $s7, 28($sp)
addi $sp, $sp, -4
sw $fp, 0($sp)
addi $sp, $sp, -4
sw $ra, 0($sp)
li $v0, 9
la $a0, 8
syscall
move $t2, $v0
lw $t3, 44($sp)
addi $t1, $zero, 2
mult $t0, $t1
mflo $t0
li $v0, 9
la $a0, 40
syscall
move $t4, $v0
lw $ra, 0($sp)
addi $sp, $sp, 4
lw $fp, 0($sp)
addi $sp, $sp, 4
addi $sp, $sp, 32
lw $s7, 0($sp)
lw $s6, -4($sp)
lw $s5, -8($sp)
lw $s4, -12($sp)
lw $s3, -16($sp)
lw $s2, -20($sp)
lw $s1, -24($sp)
lw $s0, -28($sp)
sw $t0, 0($sp)
jr $ra
