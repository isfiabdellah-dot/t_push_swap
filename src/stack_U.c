/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   stack_U.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: aisfi <marvin@42.fr>                       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/20 11:10:00 by aisfi             #+#    #+#             */
/*   Updated: 2026/11/28 18:30:53 by aisfi            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "../header/push_swap.h"

t_ctr	*ctr_int(int cap)//valid
{
	t_ctr	*c;

	c = malloc(sizeof(t_ctr));
	if (!c)
		return (NULL);
	ft_bzero(c, sizeof(t_ctr));
	c->a = stack_init(cap);
	if (!c->a)
	{
		free(c);
		return (NULL);
	}
	c->b = stack_init(cap);
	if (!c->b)
	{
		stack_free(c->a);
		free(c);
		return (NULL);
	}
	return (c);
}

t_stack	*stack_init(int cap)//valid
{
	t_stack	*s;

	s = malloc(sizeof(t_stack));
	if (!s)
		return (NULL);
	s->arr = malloc(sizeof(int) * cap);
	if (!s->arr)
	{
		free(s);
		return (NULL);
	}
	s->capacity = cap;
	s->size = 0;
	s->head = 0;
	return (s);
}

int	stack_shift_up(t_stack *s)//valid
{
	int	tmp;

	if (s->size >= 2)
	{
		tmp = s->arr[s->head];
		s->arr[(s->head + s->size) % s->capacity] = tmp;
		s->head = (s->head + 1) % s->capacity;
		return (1);
	}
	return (0);
}

int	stack_shift_down(t_stack *s)//valid
{
	int	tmp;

	if (s->size >= 2)
	{
		tmp = s->arr[(s->head + s->size - 1) % s->capacity];
		s->head = (s->head - 1 + s->capacity) % s->capacity;
		s->arr[s->head] = tmp;
		return (1);
	}
	return (0);
}

int	stack_is_sorted(t_stack *s)//valid
{
	int	i;
	int	first;
	int	second;

	i = 0;
	while (i < s->size - 1)
	{
		first = s->arr[(s->head + i) % s->capacity];
		second = s->arr[(s->head + i + 1) % s->capacity];
		if (first > second)
			return (0);
		i++;
	}
	return (1);
}
