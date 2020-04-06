
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $sp, $sp, -4
sw $zero, 0($sp)
addi $sp, $sp, -4
sw $zero, 0($sp)
lw $t0, 0($sp)
move $t0, v
sw $t0, 0($sp)
lw $t0, 4($sp)
lw $t1, 0($sp)
addi $t0, $t1, 100
sw $t0, 4($sp)
sw $t1, 0($sp)
lw $t0, 8($sp)
li $t0, 0
sw $t0, 8($sp)
CONVERT_ARRAY_ASSIGN_LOOP:
lw $t0, 0($sp)
lw $t1, 4($sp)
bge $t0, $t1
sw $t0, 0($sp)
sw $t1, 4($sp)
lw $t0, 8($sp)
lw $t1, 0($sp)
sw $t0, None($t1)
sw $t0, 8($sp)
sw $t1, 0($sp)
lw $t1, 0($sp)
addi $t1, $t1, 4
sw $t1, 0($sp)
j, CONVERT_ARRAY_ASSIGN_LOOP
lw $t0, 12($sp)
addi $t0, zero, 10
sw $t0, 12($sp)
lw $t0, 16($sp)
addi $t0, zero, 0
sw $t0, 16($sp)
nop
lw $t0, 20($sp)
addi $t0, zero, 0
sw $t0, 20($sp)
L0:
lw $t0, 20($sp)
lw $t1, 24($sp)
bge $t0, $t1
sw $t0, 20($sp)
sw $t1, 24($sp)
nop
lw $t1, 28($sp)
lw $t2, 20($sp)
add $t1, $t1, $t2
sw $t1, 28($sp)
sw $t2, 20($sp)
lw $t0, 32($sp)
lw $t1, 28($sp)
sw $t0, None($t1)
sw $t0, 32($sp)
sw $t1, 28($sp)
lw $t1, 28($sp)
lw $t2, 20($sp)
sub $t1, $t1, $t2
sw $t1, 28($sp)
sw $t2, 20($sp)
lw $t0, 36($sp)
addi $t0, zero, 0
sw $t0, 36($sp)
L1:
lw $t0, 36($sp)
lw $t1, 32($sp)
bge $t0, $t1
sw $t0, 36($sp)
sw $t1, 32($sp)
nop
lw $t0, 12($sp)
lw $t1, 20($sp)
mult $t0, $t1
sw $t0, 12($sp)
sw $t1, 20($sp)
lw $t0, 40($sp)
mflo $t0
sw $t0, 40($sp)
lw $t1, 40($sp)
lw $t2, 36($sp)
add $t1, $t1, $t2
sw $t1, 40($sp)
sw $t2, 36($sp)
lw $t1, 44($sp)
lw $t2, 40($sp)
add $t1, $t1, $t2
sw $t1, 44($sp)
sw $t2, 40($sp)
lw $t0, 48($sp)
lw $t1, 44($sp)
sw $t0, None($t1)
sw $t0, 48($sp)
sw $t1, 44($sp)
lw $t1, 44($sp)
lw $t2, 40($sp)
sub $t1, $t1, $t2
sw $t1, 44($sp)
sw $t2, 40($sp)
lw $t1, 36($sp)
addi $t1, $t1, 1
sw $t1, 36($sp)
j, L1
L2:
lw $t1, 20($sp)
addi $t1, $t1, 1
sw $t1, 20($sp)
j, L0
EOI:
lw $t0, 52($sp)
addi $t0, zero, 1
sw $t0, 52($sp)
lw $t0, 52($sp)
lw $t1, 56($sp)
sw $t0, 0($t1)
sw $t0, 52($sp)
sw $t1, 56($sp)
lw $t0, 60($sp)
addi $t0, zero, 0
sw $t0, 60($sp)
lw $t0, 60($sp)
lw $t1, 64($sp)
sw $t0, 0($t1)
sw $t0, 60($sp)
sw $t1, 64($sp)
lw $t0, 68($sp)
lw $t1, 72($sp)
lw $t0, 0($t1)
sw $t0, 68($sp)
sw $t1, 72($sp)
lw $t0, 76($sp)
addi $t0, zero, 0
sw $t0, 76($sp)
lw $t0, 20($sp)
lw $t1, 76($sp)
move $t0, $t1
sw $t0, 20($sp)
sw $t1, 76($sp)
lw $t0, 36($sp)
addi $t0, zero, 1
sw $t0, 36($sp)
L3:
lw $t0, 20($sp)
lw $t1, 36($sp)
beq $t0, $t1
sw $t0, 20($sp)
sw $t1, 36($sp)
lw $t1, 64($sp)
lw $t2, 20($sp)
add $t1, $t1, $t2
sw $t1, 64($sp)
sw $t2, 20($sp)
lw $t0, 80($sp)
lw $t1, 64($sp)
lw $t0, None($t1)
sw $t0, 80($sp)
sw $t1, 64($sp)
lw $t1, 64($sp)
lw $t2, 20($sp)
sub $t1, $t1, $t2
sw $t1, 64($sp)
sw $t2, 20($sp)
lw $t0, 76($sp)
lw $t1, 20($sp)
addi $t0, $t1, 1
sw $t0, 76($sp)
sw $t1, 20($sp)
lw $t0, 20($sp)
lw $t1, 76($sp)
move $t0, $t1
sw $t0, 20($sp)
sw $t1, 76($sp)
lw $t1, 28($sp)
lw $t2, 80($sp)
add $t1, $t1, $t2
sw $t1, 28($sp)
sw $t2, 80($sp)
lw $t0, 32($sp)
lw $t1, 28($sp)
lw $t0, None($t1)
sw $t0, 32($sp)
sw $t1, 28($sp)
lw $t1, 28($sp)
lw $t2, 80($sp)
sub $t1, $t1, $t2
sw $t1, 28($sp)
sw $t2, 80($sp)
lw $t0, 84($sp)
lw $t1, 20($sp)
move $t0, $t1
sw $t0, 84($sp)
sw $t1, 20($sp)
lw $t0, 84($sp)
addi $t0, zero, 0
sw $t0, 84($sp)
L4:
lw $t0, 84($sp)
lw $t1, 32($sp)
bge $t0, $t1
sw $t0, 84($sp)
sw $t1, 32($sp)
lw $t0, 40($sp)
lw $t1, 84($sp)
move $t0, $t1
sw $t0, 40($sp)
sw $t1, 84($sp)
lw $t0, 12($sp)
lw $t1, 80($sp)
mult $t0, $t1
sw $t0, 12($sp)
sw $t1, 80($sp)
lw $t0, 40($sp)
mflo $t0
sw $t0, 40($sp)
lw $t1, 40($sp)
lw $t2, 84($sp)
add $t1, $t1, $t2
sw $t1, 40($sp)
sw $t2, 84($sp)
lw $t1, 44($sp)
lw $t2, 40($sp)
add $t1, $t1, $t2
sw $t1, 44($sp)
sw $t2, 40($sp)
lw $t0, 48($sp)
lw $t1, 44($sp)
lw $t0, None($t1)
sw $t0, 48($sp)
sw $t1, 44($sp)
lw $t1, 44($sp)
lw $t2, 40($sp)
sub $t1, $t1, $t2
sw $t1, 44($sp)
sw $t2, 40($sp)
lw $t1, 56($sp)
lw $t2, 48($sp)
add $t1, $t1, $t2
sw $t1, 56($sp)
sw $t2, 48($sp)
lw $t0, 88($sp)
lw $t1, 56($sp)
lw $t0, None($t1)
sw $t0, 88($sp)
sw $t1, 56($sp)
lw $t1, 56($sp)
lw $t2, 48($sp)
sub $t1, $t1, $t2
sw $t1, 56($sp)
sw $t2, 48($sp)
lw $t0, 88($sp)
lw $t1, 92($sp)
beq $t0, $t1
sw $t0, 88($sp)
sw $t1, 92($sp)
lw $t0, 96($sp)
addi $t0, 1
sw $t0, 96($sp)
lw $t1, 56($sp)
lw $t2, 48($sp)
add $t1, $t1, $t2
sw $t1, 56($sp)
sw $t2, 48($sp)
lw $t0, 100($sp)
lw $t1, 56($sp)
sw $t0, None($t1)
sw $t0, 100($sp)
sw $t1, 56($sp)
lw $t1, 56($sp)
lw $t2, 48($sp)
sub $t1, $t1, $t2
sw $t1, 56($sp)
sw $t2, 48($sp)
lw $t1, 64($sp)
lw $t2, 36($sp)
add $t1, $t1, $t2
sw $t1, 64($sp)
sw $t2, 36($sp)
lw $t0, 48($sp)
lw $t1, 64($sp)
sw $t0, None($t1)
sw $t0, 48($sp)
sw $t1, 64($sp)
lw $t1, 64($sp)
lw $t2, 36($sp)
sub $t1, $t1, $t2
sw $t1, 64($sp)
sw $t2, 36($sp)
lw $t1, 56($sp)
lw $t2, 48($sp)
add $t1, $t1, $t2
sw $t1, 56($sp)
sw $t2, 48($sp)
lw $t0, 68($sp)
lw $t1, 56($sp)
lw $t0, None($t1)
sw $t0, 68($sp)
sw $t1, 56($sp)
lw $t1, 56($sp)
lw $t2, 48($sp)
sub $t1, $t1, $t2
sw $t1, 56($sp)
sw $t2, 48($sp)
lw $t1, 36($sp)
addi $t1, $t1, 1
sw $t1, 36($sp)
L6:
lw $t1, 84($sp)
addi $t1, $t1, 1
sw $t1, 84($sp)
j, L4
L5:
j, L3
FIN:
lw $t0, 76($sp)
addi $t0, zero, 0
sw $t0, 76($sp)
lw $t0, 20($sp)
lw $t1, 76($sp)
move $t0, $t1
sw $t0, 20($sp)
sw $t1, 76($sp)
L7:
lw $t0, 20($sp)
lw $t1, 36($sp)
beq $t0, $t1
sw $t0, 20($sp)
sw $t1, 36($sp)
lw $t1, 64($sp)
lw $t2, 20($sp)
add $t1, $t1, $t2
sw $t1, 64($sp)
sw $t2, 20($sp)
lw $t0, 48($sp)
lw $t1, 64($sp)
lw $t0, None($t1)
sw $t0, 48($sp)
sw $t1, 64($sp)
lw $t1, 64($sp)
lw $t2, 20($sp)
sub $t1, $t1, $t2
sw $t1, 64($sp)
sw $t2, 20($sp)
nop
nop
lw $t0, 76($sp)
lw $t1, 20($sp)
addi $t0, $t1, 1
sw $t0, 76($sp)
sw $t1, 20($sp)
lw $t0, 20($sp)
lw $t1, 76($sp)
move $t0, $t1
sw $t0, 20($sp)
sw $t1, 76($sp)
j, L7
L8: