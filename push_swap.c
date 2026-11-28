/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   push_swap.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nguerrab <nguerrab@student.1337.ma>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/24 15:31:12 by nguerrab          #+#    #+#             */
/*   Updated: 2026/11/28 18:45:35 by aisfi            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "header/push_swap.h"

void	push_swap(t_ctr *s, int flag)
{
	if (stack_is_sorted(s->a))
		return ;
	disorder(s);
	if (flag == 0 || flag == 4)
	{
		if (s->disorder < 0.2)
		{
			select_sort(s);
			s->strategy = ft_strdup("Adaptive / O(n\u00B2)");
		}
		else if (s->disorder >= 0.2 && s->disorder < 0.5)
		{
			chunk_sort(s);
			s->strategy = ft_strdup("Adaptive / O(n\u221An)");
		}
		else
		{
			radix_sort(s);
			s->strategy = ft_strdup("Adaptive / O(nlog(n))");
		}
	}
	else
	{
		if (flag == 1)
		{
			select_sort(s);
			s->strategy = ft_strdup("Simple / O(n\u00B2)");
		}
		else if (flag == 2)
		{
			chunk_sort(s);
			s->strategy = ft_strdup("Medium / O(n\u221An)");
		}
		else
		{
			radix_sort(s);
			s->strategy = ft_strdup("Complex / O(nlog(n))");
		}
	}
}
