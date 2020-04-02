main:
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $t1, $zero, 1
addi $t0, $zero, 2
addi $sp, $sp, -4
sw $t2, 0($sp)
lw $t2, 4($sp)
addi $t2, $zero, 4
sw $t2, 4($sp)
lw $t2, 0($sp)
addi $sp, $sp, 4
add $t2, $t1, $t0
sub $t0, $t2, $t1
addi $sp, $sp, -4
sw $t1, 0($sp)
lw $t1, 4($sp)
addi $t2, $t1, 3
sw $t1, 4($sp)
lw $t1, 0($sp)
addi $sp, $sp, 4
add $t1, $t1, $t1
add $t2, $t0, $t1
addi $sp, $sp, -4
sw $t1, 0($sp)
lw $t1, 4($sp)
add $t1, $t0, $t2
sw $t1, 4($sp)
lw $t1, 0($sp)
addi $sp, $sp, 4
addi $sp, $sp, -4
sw $t2, 0($sp)
lw $t2, 4($sp)
add $a0, $zero, $t2
sw $t2, 4($sp)
lw $t2, 0($sp)
addi $sp, $sp, 4
end:
j, end