/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   op_stack.c                                         :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: aisfi <marvin@42.fr>                       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/20 09:59:40 by aisfi             #+#    #+#             */
/*   Updated: 2026/11/28 17:32:51 by aisfi            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "../header/push_swap.h"

void	pa(t_ctr *s)//valide
{
	int	val;

	if (s->a->size >= s->a->capacity || s->b->size < 1)
		return ;
	if (stack_pop(s->b, &val) == 0)
		return ;
	stack_push(val, s->a);
	s->pa++;
	write(1, "pa\n", 3);
}

void	pb(t_ctr *s)//valide
{
	int	val;

	if (s->b->size >= s->b->capacity || s->a->size < 1)
		return ;
	stack_pop(s->a, &val);
	stack_push(val, s->b);
	s->pb++;
	write(1, "pb\n", 3);
}

void	sa(t_ctr *s)//valid
{
	if (s->a->size < 2)
		return ;
	stack_swap(s->a);
	s->sa++;
	write(1, "sa\n", 3);
}

void	sb(t_ctr *s)//valid
{
	if (s->b->size < 2)
		return ;
	stack_swap(s->b);
	s->sb++;
	write(1, "sb\n", 3);
}

void	ss(t_ctr *s)//valid
{
	if (s->a->size < 2 && s->b->size < 2)
		return ;
	stack_swap(s->a);
	stack_swap(s->b);
	s->ss++;
	write(1, "ss\n", 3);
}
