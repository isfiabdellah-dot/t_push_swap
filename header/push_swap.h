/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   push_swap.h                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: aisfi <marvin@42.fr>                       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/19 15:46:18 by aisfi             #+#    #+#             */
/*   Updated: 2026/11/28 18:43:34 by aisfi            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PUSH_SWAP_H
# define PUSH_SWAP_H

# include <unistd.h>
# include <stdlib.h>
# include <limits.h>
# include <stdio.h>

typedef struct s_stack
{
	int	*arr;
	int	capacity;
	int	head;
	int	size;
}	t_stack;

typedef struct s_ctr
{
	t_stack	*a;
	t_stack	*b;
	float	disorder;
	char	*strategy;
	int	total_ops;
	int	sa;
	int	sb;
	int	ss;
	int	pa;
	int	pb;
	int	ra;
	int	rb;
	int	rr;
	int	rra;
	int	rrb;
	int	rrr;
}	t_ctr;

int		stack_is_sorted(t_stack *s);
int		stack_pop(t_stack *s, int *val);
int		stack_shift_up(t_stack *s);
int		stack_shift_down(t_stack *s);
int		isallnum(char *av);
int		ft_memcmp(void *s1, void *s2, int n);
int		ft_strlen(const char *str);
int		isnum(char *av);
int		repetition(t_ctr *s, int n, int *i);
int		valid_add(char *av, t_ctr *s, int *i);
int		add_to(t_ctr *s, int ac, char **av);
int		sqre(int n);
int		fft_max(t_stack *s);
int		ft_index(int n, int *arr, t_stack *a);
int		*ranking(t_stack *a);
char	*ft_strdup(const char *s);
void	bench(t_ctr *s);
void	ft_bzero(void *s, size_t n);
void	push_swap(t_ctr *s, int flag);
void	chunk_sort(t_ctr *s);
void	ifelse(int flag, int argc, char **argv, t_ctr *s);
void	error(void);
void	print_arr(t_stack *s);
void	ft_putnbr(int n);	
void	stack_swap(t_stack *s);
void	stack_push(int val, t_stack *s);
void	stack_free(t_stack *s);
void	pa(t_ctr *s);
void	pb(t_ctr *s);
void	sa(t_ctr *s);
void	sb(t_ctr *s);
void	ss(t_ctr *s);
void	ra(t_ctr *s);
void	rb(t_ctr *s);
void	rr(t_ctr *s);
void	rra(t_ctr *s);
void	rrb(t_ctr *s);
void	rrr(t_ctr *s);
void	select_sort(t_ctr *s);
void    chunk_sort(t_ctr *s);
void    radix_sort(t_ctr *s);
void	disorder(t_ctr *s);
t_ctr	*ctr_int(int cap);
t_stack	*stack_init(int cap);

#endif
