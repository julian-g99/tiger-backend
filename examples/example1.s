main:
li      $v0, 9
la      $a0, 8
syscall
move    $t0, $v0

addi    $t1, $zero, 3
sw      $t1, 0($t0)

addi    $t1, $t1, 1
sw      $t1, 4($t0)

lw      $t3, 0($t0)
lw      $t4, 4($t0)

li      $v0, 10
syscall