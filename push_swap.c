/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   push_swap.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: nguerrab <nguerrab@student.1337.ma>        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/24 15:31:12 by nguerrab          #+#    #+#             */
/*   Updated: 2026/11/27 15:19:02 by aisfi            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "header/push_swap.h"

void	push_swap(t_ctr *s, int flag, float disorder)
{
	if (flag == 0 || flag == 4)
	{
		if (disorder < 0.2)
		{
			select_sort(s);
			printf("\n %f \n", disorder);
			printf("bubble_sort >> flag 0");
		}
		else if (disorder >= 0.2 && disorder < 0.5)
		{
			chunk_sort(s);
			printf("\n %f \n", disorder);
			printf("chunk_sort  >> flag 0");
		}
		else
		{
			radix_sort(s);
			printf("\n n log n \n >> %f", disorder);
			printf("radix_sort  >> flag  3");
		}
	}
	else
	{
		if (flag == 1)
		{
			select_sort(s);
			printf("\n %f \n", disorder);
			printf("bubble_sort  >> flag 1");
		}
		else if (flag == 2)
		{
			chunk_sort(s);
			printf("\n %f \n", disorder);
			printf("chunk_sort  >> flag  2");
		}
		else
		{
			radix_sort(s);
			printf("\n n log n \n >> %f", disorder);
			printf("radix_sort  >> flag  3");
		}
	}
	print_arr(s->a);
}
